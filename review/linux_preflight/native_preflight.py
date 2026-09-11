"""Real Linux checks of the reviewed runner, using development data only.

Run from the repository: python review/linux_preflight/native_preflight.py --output NEW_DIRECTORY
No shim is imported. Scientific configuration/source files are never edited.
Short time and disk limits are explicit operational fixtures in child processes.
"""

import argparse
import errno
import inspect
import json
import mmap
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/geometric_waste_predictive_v2"
sys.path.insert(0, str(EXPERIMENT))
import runner
import resource
import signal

CODE_COMMIT = "584b79500e912dffc17e03832802ac6a94f7bb45"


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def file_hashes(directory):
    return {str(p.relative_to(directory)): runner.digest(p)
            for p in directory.rglob("*") if p.is_file()}


def probe(case, output):
    check(sys.platform == "linux", "This check requires native Linux")
    check(resource.__spec__ is not None and
          (resource.__spec__.origin == "built-in" or resource.__spec__.origin.endswith(".so"))
          and inspect.isbuiltin(resource.setrlimit),
          "Expected real CPython resource extension, not a shim")
    config = runner.load_config()["execution"].copy()
    original_limit = resource.getrlimit(resource.RLIMIT_AS)
    original_handler = signal.getsignal(signal.SIGALRM)
    if case == "interruption_resume":
        run = output / "development_interrupted"
        original_loader = runner.load_config
        fixture = original_loader()
        fixture["execution"]["batch_active_seconds_max"] = 0.03
        runner.load_config = lambda: fixture
        args = argparse.Namespace(stage="development", output=run, resume=False,
                                  reviews=None, code_commit=CODE_COMMIT)
        interrupted = False
        try:
            runner.execute(args)
        except TimeoutError:
            interrupted = True
        finally:
            runner.load_config = original_loader
        check(interrupted, "The operational 30 ms fixture should interrupt this full development run")
        batches = [runner.read(p) for p in run.glob("batch-*.json")]
        check(len(batches) == 1 and batches[0]["status"] == "incomplete", "Incomplete batch not recorded")
        check(not (run / "development.json").exists(), "Interrupted run incorrectly completed")
        before = file_hashes(run)
        args.resume = True
        runner.execute(args)
        after = file_hashes(run)
        check(all(after[k] == v for k, v in before.items()), "Resume replaced an existing checkpoint")
        from audit_development import audit
        verified = audit(run)
        check(resource.getrlimit(resource.RLIMIT_AS) == original_limit, "Memory limit not restored")
        check(signal.getsignal(signal.SIGALRM) == original_handler, "Signal handler not restored")
        return {"status":"passed", "time_fixture_seconds":0.03,
                "interrupted_status":"incomplete", "resume_status":"completed",
                "existing_files_preserved":len(before), "audit":verified,
                "final_file_hashes":after,
                "resource_batches":[runner.read(p) for p in sorted(run.glob("batch-*.json"))]}
    if case == "timer":
        config["batch_active_seconds_max"] = 0.05
    if case == "disk":
        config["output_gib_max"] = 96 * 1024 / 1024**3
    budget = runner.Budget(config, output)
    start = time.monotonic()
    try:
        if case == "memory":
            active = resource.getrlimit(resource.RLIMIT_AS)[0]
            check(0 < active <= 4 * 1024**3, "4 GiB ceiling was not installed")
            allocation_rejected = False
            try:
                # Reserve virtual address space without touching physical pages.
                allocation = mmap.mmap(-1, active)
            except OSError as exc:
                check(exc.errno == errno.ENOMEM, "Unexpected mmap error: " + str(exc))
                allocation_rejected = True
            else:
                allocation.close()
            check(allocation_rejected, "Address-space limit did not reject oversized mapping")
            result = {"status":"passed", "active_rlimit_as_bytes":active,
                      "oversized_virtual_mapping":"rejected_ENOMEM"}
        elif case == "timer":
            delivered = False
            try:
                time.sleep(2)  # No Budget.check call: exercise actual SIGALRM delivery.
            except TimeoutError as exc:
                check("resume the same stage" in str(exc), "Wrong timeout path")
                delivered = True
            check(delivered, "The real SIGALRM handler was not invoked")
            result = {"status":"passed", "configured_seconds":0.05,
                      "elapsed_seconds":time.monotonic()-start, "real_SIGALRM_delivered":True}
        elif case == "disk":
            runner.ACTIVE_BUDGET = budget
            saved = output / "preserved.json"
            runner.write_once(saved, {"keep":True})
            original = saved.read_bytes()
            refused = False
            try:
                runner.write_once(output / "too_large.json", {"payload":"x"*32768})
            except RuntimeError as exc:
                check("storage limit" in str(exc), "Wrong disk preflight exception")
                refused = True
            check(refused and not (output / "too_large.json").exists(), "Oversized output was published")
            check(saved.read_bytes() == original, "Existing output changed")
            check(not list(output.glob("*.partial-*")), "Unpublished partial file was left by refusal")
            runner.ACTIVE_BUDGET = None
            # Simulate external disk consumption, outside the guarded writer.
            (output / "external_filler.bin").write_bytes(b"x"*budget.disk_limit)
            detected = False
            try:
                budget.check()
            except RuntimeError as exc:
                check("storage limit" in str(exc), "Wrong full-directory error")
                detected = True
            check(detected, "Budget.check did not detect an over-limit directory")
            result = {"status":"passed", "disk_fixture_bytes":budget.disk_limit,
                      "preflight_refused":True, "existing_file_preserved":True,
                      "external_over_limit_detected":True}
        else:
            raise ValueError(case)
    finally:
        runner.ACTIVE_BUDGET = None
        budget.close()
    check(resource.getrlimit(resource.RLIMIT_AS) == original_limit, "Memory limit not restored")
    check(signal.getsignal(signal.SIGALRM) == original_handler, "Signal handler not restored")
    check(signal.getitimer(signal.ITIMER_REAL)[0] == 0, "Timer not cancelled")
    return dict(result, memory_limit_restored=True, signal_handler_restored=True, timer_cancelled=True)


def main(args):
    if args.child:
        result = probe(args.child, args.output)
        runner.write_once(args.output / "probe.json", result)
        return
    args.output.mkdir(parents=True, exist_ok=False)
    results = {}
    for case in ("memory", "timer", "disk", "interruption_resume"):
        directory = args.output / case
        directory.mkdir()
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                    "--child", case, "--output", str(directory.resolve())],
                                   capture_output=True, text=True, timeout=30)
        (directory / "stdout.txt").write_text(completed.stdout)
        (directory / "stderr.txt").write_text(completed.stderr)
        check(completed.returncode == 0, case + " failed: " + completed.stderr)
        results[case] = runner.read(directory / "probe.json")
    evidence = runner.verify_reviews(ROOT / "review/reviews.json", runner.load_config())
    result = {"status":"passed", "platform":platform.platform(),
              "python":platform.python_version(), "numpy":runner.np.__version__,
              "resource_module":resource.__spec__.origin, "probes":results,
              "source_hashes":{name:runner.digest(EXPERIMENT/name) for name in
                               ("runner.py","model.py","protocol.json","PROTOCOL.md")},
              "review_evidence_verified":{k:evidence[k]["verdict"] for k in ("G01","implementation")},
              "probe_script_sha256":runner.digest(__file__),
              "confirmatory_prepare_or_evaluate_executed":False,
              "scientific_test_states_generated":False}
    runner.write_once(args.output / "native_results.json", result)
    print(json.dumps({"status":"passed", "probes":list(results),
                      "result":str(args.output / "native_results.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--child", choices=("memory","timer","disk","interruption_resume"))
    main(parser.parse_args())
