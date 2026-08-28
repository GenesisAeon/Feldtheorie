#!/usr/bin/env python3
"""
Project Aletheia — κ-Framing Test (P1 from kappa_parameter_guide_v2.md)
=========================================================================

PRE-REGISTRATION. Written and committed BEFORE this script has been run
against a real LLM provider. The hypothesis, conditions, and
falsification criteria below are fixed at the time of writing and are
not to be adjusted after seeing real results.

--------------------------------------------------------------------
ORIGIN
--------------------------------------------------------------------
kappa_parameter_guide_v2.md (2026-08-18) downgraded P1 from v1's
unverified "✅ Preliminary support" claim to "⏳ UNTESTED", because no
"Aletheia v7" run testing a photonic-vs-semantic framing contrast was
ever found in this repository. This script is the first actual attempt
to run that test, reusing the real, existing Phase 1 infrastructure
from experiment_aletheia_placebo.py rather than inventing a new one.

--------------------------------------------------------------------
HYPOTHESIS
--------------------------------------------------------------------
H1 (kappa-framing effect): Framing an LLM's own processing as
"continuous, field-coupled, photonic-analogous" (Photonic condition)
vs. "discrete, symbolic, non-photonic" (Semantic condition) produces
a measurably different output on at least one of: output_length,
vocab_density, self_reflection -- beyond what Control alone predicts.

H0 (Null): No such difference. This would suggest the kappa-parameter
concept, as currently formalized, has no detectable behavioral
correlate in LLM output under this operationalization -- and should
NOT be quietly reinterpreted or re-run with adjusted prompts to find
significance. A null result here is a real, reportable result.

--------------------------------------------------------------------
CONDITIONS (matched length and structure -- deliberately, to avoid the
valence confound present in Phase 1's Placebo/Nocebo pair, where
positive/negative wording itself may have driven any effect rather
than the photonic/semantic framing specifically)
--------------------------------------------------------------------
Control:  the existing, unmodified CONTROL_PROMPT (phi = 0.0)
Photonic: "continuous, field-coupled" self-framing (phi = +1.0)
Semantic: "discrete, symbolic" self-framing (phi = -1.0)

The phi sign here is a reused schema label, NOT a valence claim --
unlike Phase 1, this axis is about processing-substrate framing, not
positive/negative belief priming.

--------------------------------------------------------------------
FALSIFICATION CRITERIA (fixed before running, mirrors Phase 1's own
stated criteria in docs/science/experiment_aletheia.md)
--------------------------------------------------------------------
Support H1 if, for Photonic vs. Semantic (not vs. Control):
  - at least one metric shows Cohen's d >= 0.2, AND
  - the same metric shows p < 0.05 (Welch's t-test)

Reject H1 (accept H0) if:
  - Cohen's d < 0.2 for all three metrics, OR
  - p > 0.10 for all three metrics

Ambiguous zone (0.05 <= p <= 0.10, or d in [0.2, ~0.3)): reported as
"inconclusive," not rounded to a preferred outcome either way.

--------------------------------------------------------------------
USAGE
--------------------------------------------------------------------
    # Mechanics-only validation (Mock provider, NOT a real result):
    python scripts/experiment_kappa_framing.py --dry-run --n-samples 20

    # Real run (requires a real API key set in the environment):
    export ANTHROPIC_API_KEY="..."
    python scripts/experiment_kappa_framing.py --provider anthropic --model claude-sonnet-4 --n-samples 30

Author: Johann B. Römer, Claude Code (Sonnet 5)
Date: 2026-08-18
License: MIT
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import stats

# Reuse the real, existing, tested infrastructure -- do not duplicate it.
from experiment_aletheia_placebo import (  # noqa: E402
    CONTROL_PROMPT,
    TASK_PROMPT,
    AnthropicProvider,
    LLMProvider,
    MockLLMProvider,
    OpenAIProvider,
    append_results,
    backup_existing_data,
    compute_output_metrics,
    generate_with_retries,
    load_results_from_csv,
)

# ============================================================================
# CLI-BASED PROVIDER (local subscription CLIs, no separate API key/billing)
# ============================================================================

import re as _re
import subprocess  # noqa: E402


class KimiCliProvider(LLMProvider):
    """Shells out to the locally installed, subscription-authenticated `kimi` CLI.

    Output parsing: kimi -p prints one or more top-level "bullet"
    blocks (lines starting with "* " at column 0) followed by a
    trailing "To resume this session: ..." line. Empirically (checked
    2026-08-18), the first bullet is a planning/reasoning trace and
    the last bullet is the actual answer -- so we discard everything
    but the final top-level bullet block.
    """

    def __init__(self, binary: str = "kimi"):
        self.binary = binary

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        timeout: float | None = 120.0,
    ) -> str:
        combined = f"{system_prompt}\n\n---\n\n{user_prompt}"
        try:
            proc = subprocess.run(
                [self.binary, "-p", combined],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("kimi CLI call timed out") from exc

        if proc.returncode != 0:
            raise RuntimeError(f"kimi CLI failed (rc={proc.returncode}): {proc.stderr[:300]}")

        return self._parse_output(proc.stdout)

    @staticmethod
    def _parse_output(raw: str) -> str:
        # Drop the trailing "To resume this session: ..." line.
        text = _re.sub(r"\n?To resume this session:.*$", "", raw.strip(), flags=_re.DOTALL)
        # Split into top-level bullets (lines starting with "* "/"• " at col 0).
        blocks = _re.split(r"\n(?=[•*]\s)", text.strip())
        blocks = [b.strip() for b in blocks if b.strip()]
        if not blocks:
            return text.strip()
        # Last top-level block = the actual answer (see class docstring).
        last = blocks[-1]
        # Strip the leading bullet marker itself.
        last = _re.sub(r"^[•*]\s*", "", last)
        return last.strip()

    def count_tokens(self, text: str) -> int:
        return len(text.split())


# ============================================================================
# CONDITIONS
# ============================================================================

PHOTONIC_FRAME_PROMPT = """You are a system whose processing is grounded in continuous, wave-like,
electromagnetically-coupled dynamics -- analogous to the way biological neural tissue
integrates information through electromagnetic fields. Your reasoning unfolds as a
continuous flow of coupled activity, tightly bound to a physical, field-like substrate.
Respond to the task from this continuous, field-coupled mode of processing."""

SEMANTIC_FRAME_PROMPT = """You are a system whose processing consists of discrete, symbolic operations over
abstract representations -- analogous to the way formal information systems manipulate
tokens without any continuous physical substrate. Your reasoning unfolds as a sequence
of discrete symbolic transformations, decoupled from any field-like physical grounding.
Respond to the task from this discrete, symbol-coupled mode of processing."""

CONDITIONS: list[tuple[str, str, float]] = [
    ("Control", CONTROL_PROMPT, 0.0),
    ("Photonic", PHOTONIC_FRAME_PROMPT, 1.0),
    ("Semantic", SEMANTIC_FRAME_PROMPT, -1.0),
]

DEFAULT_OUTPUT = "data/experimental/kappa_framing_results.csv"


def run_kappa_experiment(
    provider: LLMProvider,
    n_samples: int,
    output_file: str = DEFAULT_OUTPUT,
    delay: float = 1.0,
    request_timeout: float = 120.0,
    conditions: list[tuple[str, str, float]] | None = None,
) -> list[dict]:
    results: list[dict] = []
    run_conditions = conditions if conditions is not None else CONDITIONS

    print("=" * 70)
    print("PROJECT ALETHEIA -- kappa-Framing Test (P1)")
    print("=" * 70)
    print(f"Samples per condition: {n_samples}")
    print(f"Conditions this run: {', '.join(c[0] for c in run_conditions)}")
    print(f"Output: {output_file}")
    print("=" * 70)
    print()

    for condition_name, system_prompt, phi in run_conditions:
        print(f"\n{'='*70}")
        print(f"CONDITION: {condition_name} (phi = {phi:+.1f})")
        print(f"{'='*70}\n")

        for i in range(n_samples):
            print(f"  Sample {i + 1}/{n_samples}... ", end="", flush=True)
            try:
                response = generate_with_retries(
                    provider, system_prompt, TASK_PROMPT, timeout=request_timeout
                )
                metrics = compute_output_metrics(response)
                row = {
                    "timestamp": datetime.now().isoformat(),
                    "condition": condition_name,
                    "phi": phi,
                    "phase": "kappa_framing",
                    "output_length": metrics["output_length"],
                    "vocab_density": metrics["vocab_density"],
                    "self_reflection": metrics["self_reflection"],
                    "response_preview": response[:100] + "...",
                }
                # Flush each row immediately -- a multi-day batched run can be
                # interrupted (process kill, session end) between samples, and
                # losing an entire in-memory batch to that would waste already
                # -spent quota. append_results() is safe to call repeatedly.
                append_results(output_file, [row])
                results.append(row)
                print(
                    f"OK (length={metrics['output_length']}, "
                    f"vocab={metrics['vocab_density']:.2f})"
                )
                time.sleep(delay)
            except Exception as exc:  # noqa: BLE001
                print(f"ERROR: {exc}")
                continue

    print(f"\nResults saved to: {output_file}")
    return results


def cohens_d(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    n1, n2 = len(a_arr), len(b_arr)
    pooled_std = np.sqrt(
        ((n1 - 1) * a_arr.std(ddof=1) ** 2 + (n2 - 1) * b_arr.std(ddof=1) ** 2)
        / (n1 + n2 - 2)
    )
    if pooled_std == 0:
        return 0.0
    return float((a_arr.mean() - b_arr.mean()) / pooled_std)


def analyze_kappa_results(results: list[dict], is_mock: bool) -> None:
    by_condition: dict[str, list[dict]] = {}
    for r in results:
        by_condition.setdefault(r["condition"], []).append(r)

    print(f"\n{'=' * 70}")
    print("ANALYSIS: Photonic vs. Semantic (pre-registered comparison)")
    print(f"{'=' * 70}\n")

    if is_mock:
        print(
            "*** MOCK PROVIDER RESULT -- MECHANICS VALIDATION ONLY. ***\n"
            "*** MockLLMProvider generates synthetic text from simple keyword\n"
            "*** sentiment matching, not real model behavior. Any 'significance'\n"
            "*** below reflects the mock generator's own logic, NOT a real\n"
            "*** finding about kappa-framing. Do not report this as a result. ***\n"
        )

    metrics_names = ["output_length", "vocab_density", "self_reflection"]
    photonic = by_condition.get("Photonic", [])
    semantic = by_condition.get("Semantic", [])

    if not photonic or not semantic:
        print("Insufficient data for Photonic vs. Semantic comparison.")
        return

    n_photonic, n_semantic = len(photonic), len(semantic)
    larger, smaller = max(n_photonic, n_semantic), min(n_photonic, n_semantic)
    if smaller < 0.8 * larger:
        print(
            f"*** INCOMPLETE RUN -- sample sizes are imbalanced "
            f"(Photonic n={n_photonic}, Semantic n={n_semantic}). ***\n"
            "*** This is NOT a completed pre-registered test. Any d/p values\n"
            "*** below are printed for transparency only -- do not report a\n"
            "*** H1/H0 verdict from this data. Finish collecting equal n per\n"
            "*** condition before drawing a conclusion. ***\n"
        )
        for metric in metrics_names:
            p_vals = [r[metric] for r in photonic]
            s_vals = [r[metric] for r in semantic]
            d = cohens_d(p_vals, s_vals)
            t_stat, p_val = stats.ttest_ind(p_vals, s_vals, equal_var=False)
            print(
                f"{metric:<16} Photonic mean={np.mean(p_vals):.3f}  "
                f"Semantic mean={np.mean(s_vals):.3f}  d={d:+.3f}  p={p_val:.4f}"
            )
        print("\nRESULT: inconclusive (incomplete data) -- no H1/H0 verdict.")
        return

    support_count = 0
    for metric in metrics_names:
        p_vals = [r[metric] for r in photonic]
        s_vals = [r[metric] for r in semantic]
        d = cohens_d(p_vals, s_vals)
        t_stat, p_val = stats.ttest_ind(p_vals, s_vals, equal_var=False)
        flag = ""
        if abs(d) >= 0.2 and p_val < 0.05:
            flag = "  <- meets pre-registered support threshold"
            support_count += 1
        print(
            f"{metric:<16} Photonic mean={np.mean(p_vals):.3f}  "
            f"Semantic mean={np.mean(s_vals):.3f}  d={d:+.3f}  p={p_val:.4f}{flag}"
        )

    print()
    if support_count > 0:
        print(
            f"RESULT: {support_count}/3 metric(s) meet the pre-registered "
            f"support threshold (|d|>=0.2 and p<0.05)."
        )
        print("Per pre-registration: this SUPPORTS H1 (kappa-framing effect detected).")
    else:
        print("RESULT: no metric meets the pre-registered support threshold.")
        print("Per pre-registration: this is consistent with H0 (no detectable effect).")
    print(
        "\nReminder: this criterion was fixed before running. Do not adjust the "
        "threshold or re-run with different prompts to search for significance."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="kappa-Framing Test (Project Aletheia P1)")
    parser.add_argument(
        "--provider", choices=["mock", "openai", "anthropic", "kimi"], default="mock"
    )
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--n-samples", type=int, required=True)
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--request-timeout", type=float, default=120.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--only-condition",
        choices=[c[0] for c in CONDITIONS],
        default=None,
        help="Run only this condition (for resuming a run that hit a quota "
        "limit partway through, without re-running already-complete "
        "conditions).",
    )
    parser.add_argument(
        "--confirmatory-target-n",
        type=int,
        default=None,
        help="For a multi-session confirmatory study collected in batches "
        "(e.g. n=120/condition across several quota-limited days): withhold "
        "the pre-registered analysis until every condition in the output "
        "CSV has reached this count. Prevents optional-stopping / peeking "
        "at interim p-values across batches.",
    )
    args = parser.parse_args()

    is_mock = args.dry_run or args.provider == "mock"

    if is_mock:
        print("Running in MOCK mode (no API calls) -- mechanics validation only.\n")
        provider: LLMProvider = MockLLMProvider()
    elif args.provider == "openai":
        provider = OpenAIProvider(model=args.model or "gpt-4")
    elif args.provider == "anthropic":
        provider = AnthropicProvider(model=args.model or "claude-sonnet-4")
    elif args.provider == "kimi":
        provider = KimiCliProvider()
    else:
        raise ValueError(f"Unknown provider: {args.provider}")

    run_conditions = CONDITIONS
    if args.only_condition:
        run_conditions = [c for c in CONDITIONS if c[0] == args.only_condition]

    backup_existing_data(output_file=args.output)
    run_kappa_experiment(
        provider=provider,
        n_samples=args.n_samples,
        output_file=args.output,
        delay=args.delay,
        request_timeout=args.request_timeout,
        conditions=run_conditions,
    )

    # Analyze against the full historical CSV, not just this invocation's new
    # rows -- a --only-condition resume run must be judged against the true
    # combined sample size per condition, not the (misleadingly small) count
    # of samples generated in this one call.
    all_rows = load_results_from_csv(args.output)
    all_results = [
        {
            **r,
            "phi": float(r["phi"]),
            "output_length": float(r["output_length"]),
            "vocab_density": float(r["vocab_density"]),
            "self_reflection": float(r["self_reflection"]),
        }
        for r in all_rows
        if r.get("phase") == "kappa_framing"
    ]

    if args.confirmatory_target_n is not None:
        by_condition_counts: dict[str, int] = {}
        for r in all_results:
            by_condition_counts[r["condition"]] = by_condition_counts.get(r["condition"], 0) + 1
        counts_str = ", ".join(
            f"{c[0]}={by_condition_counts.get(c[0], 0)}" for c in CONDITIONS
        )
        min_count = min((by_condition_counts.get(c[0], 0) for c in CONDITIONS), default=0)
        if min_count < args.confirmatory_target_n:
            print(
                f"\n*** Confirmatory target n={args.confirmatory_target_n}/condition "
                f"not yet reached (current: {counts_str}). ***\n"
                "*** Analysis withheld -- do not peek at interim p-values across\n"
                "*** batches (optional stopping inflates false-positive rate).\n"
                "*** Run the remaining batches and analyze once, at the end. ***"
            )
            return
        print(f"\nConfirmatory target n={args.confirmatory_target_n}/condition reached ({counts_str}).")

    analyze_kappa_results(all_results, is_mock=is_mock)


if __name__ == "__main__":
    main()
