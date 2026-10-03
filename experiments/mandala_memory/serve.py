"""M6: local service for the Mandala memory view (plan §8).

Security and data rules:
- binds to 127.0.0.1 only; no shell endpoint; the browser can never pass a
  file path -- static files come from ONE fixed directory, runs are chosen
  from enumerated, bounded parameters;
- every requested run is EXPLORATIVE: a new run id, an append-only
  protocol entry, a trace file under the explore directory; benchmark
  results and the frozen protocol are never written;
- no second physics core in JavaScript: every trace is computed here by the
  tested Python kernel (core.EpisodeOperator).

    python -m experiments.mandala_memory.serve [--port 8765] [--ui DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import mimetypes
import time
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import numpy as np

from experiments.mandala_memory import SCHEMA_VERSION
from experiments.mandala_memory.core import EpisodeOperator, MemoryLabError, one_hot
from experiments.mandala_memory.model import adapt_network, condition_specs

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "protocol" / "startkonfiguration.json").read_text(encoding="utf-8"))
DEFAULT_UI = Path(r"D:/mandala/.worktrees/unified-mandala-memory-lab/experiments/memory_lab")
EXPLORE_DIR = Path(r"D:/mandala/mandala-memory-results/explore")
NETWORKS = ("frozen", "adapted", "uncoupled_leak", "linear", "uniform_M1")
INTERVENTIONS = ("none", "clear_after_pulse")
MAX_DELAY = 64
MAX_RUNS = 4
ADAPT_SEED = int(CONFIG["smoke"]["seeds"][0])
TRACE_SCHEMA = "mandala-memory-trace-v1"


@lru_cache(maxsize=1)
def networks():
    specs = condition_specs(CONFIG["network"])
    adapted, rec = adapt_network(specs["frozen"], CONFIG["adaptation"], mode="explore", seed=ADAPT_SEED)
    specs["adapted"] = adapted
    return specs, {"seed": ADAPT_SEED, "mode": "explore", "weight_change_fro": rec.weight_change_fro}


def validate_request(req: Dict) -> List[Dict]:
    runs = req.get("runs")
    if not isinstance(runs, list) or not (1 <= len(runs) <= MAX_RUNS):
        raise MemoryLabError(f"'runs' must be a list of 1..{MAX_RUNS} run specs")
    clean = []
    for r in runs:
        if not isinstance(r, dict) or set(r) - {"network", "stimulus", "delay", "intervention"}:
            raise MemoryLabError("run spec keys: network, stimulus, delay, intervention")
        net, stim, d, iv = r.get("network", "frozen"), r.get("stimulus"), r.get("delay"), r.get("intervention", "none")
        if net not in NETWORKS or iv not in INTERVENTIONS:
            raise MemoryLabError(f"network in {NETWORKS}, intervention in {INTERVENTIONS}")
        if stim not in (0, 1) or isinstance(stim, bool):
            raise MemoryLabError("stimulus must be 0 (A) or 1 (B)")
        if not isinstance(d, int) or isinstance(d, bool) or not (0 <= d <= MAX_DELAY):
            raise MemoryLabError(f"delay must be an integer 0..{MAX_DELAY}")
        clean.append({"network": net, "stimulus": stim, "delay": d, "intervention": iv})
    return clean


def build_trace(run: Dict) -> Dict:
    specs, _ = networks()
    spec = specs[run["network"]]
    op = EpisodeOperator(spec)
    op.reset()                                       # identical initial condition x0 = 0 for every run
    states, phases, events = [op.x.tolist()], ["start"], []
    op.step(one_hot(run["stimulus"]))
    states.append(op.x.tolist())
    phases.append("stimulus")
    if run["intervention"] == "clear_after_pulse":
        op.reset()
        states.append(op.x.tolist())
        phases.append("cleared")
        events.append({"step": 1, "event": "state cleared after the stimulus (intervention)"})
    for k in range(run["delay"]):
        op.step(np.zeros(spec.n_inputs))
        states.append(op.x.tolist())
        phases.append("pause")
    phases[-1] = "readout" if run["delay"] > 0 or run["intervention"] != "none" else "stimulus+readout"
    return {"spec": run, "network_name": spec.name, "states": states, "phases": phases, "events": events,
            "readout": states[-1], "time_convention": "u_0 = stimulus, then d zero steps; readout x_(d+1)"}


def explore(req: Dict, *, write: bool = True) -> Dict:
    runs = validate_request(req)
    specs, adapt_info = networks()
    traces = [build_trace(r) for r in runs]
    if len(traces) >= 2:
        a, b = np.array(traces[0]["readout"]), np.array(traces[1]["readout"])
        sigma = float(CONFIG["observation"]["sigma"])
        l2 = float(np.linalg.norm(a - b))
        # Equal priors, full observation H = I, isotropic Gaussian noise sigma per coordinate:
        # the optimal (Bayes) accuracy is Phi(||a - b||_2 / (2 sigma)). A finite trained
        # decoder can fall below it (control K2). Uses all coordinates, unlike max |dx|.
        from statistics import NormalDist
        comparison = {"runs": [0, 1], "readout_separation_l2": l2,
                      "readout_separation_inf": float(np.max(np.abs(a - b))),
                      "observation_noise_sigma": sigma,
                      "bayes_accuracy_full_observation": NormalDist().cdf(l2 / (2 * sigma)),
                      "bayes_formula": "Phi(||x_A - x_B||_2 / (2 sigma)), equal priors, H = I, isotropic noise"}
    else:
        comparison = None
    used = sorted({r["network"] for r in runs})
    payload = {
        "schema": TRACE_SCHEMA, "core_schema": SCHEMA_VERSION, "explorative": True,
        "created_unix": time.time(), "request": {"runs": runs},
        "benchmark_config_sha256": hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode()).hexdigest(),
        "networks": {n: {"A": specs[n].A.tolist(), "module_of": list(specs[n].module_of or []),
                         "inputs": CONFIG["network"]["inputs_zero_based"], "nonlinearity": specs[n].nonlinearity}
                     for n in used},
        "adaptation_for_adapted_network": adapt_info,
        "traces": traces, "comparison": comparison,
    }
    body = json.dumps(payload, sort_keys=True, allow_nan=False).encode()
    run_id = "explore-" + hashlib.sha256(body).hexdigest()[:12]
    payload["run_id"] = run_id
    if write:
        EXPLORE_DIR.mkdir(parents=True, exist_ok=True)
        (EXPLORE_DIR / f"{run_id}.json").write_text(json.dumps(payload, allow_nan=False) + "\n", encoding="utf-8")
        with (EXPLORE_DIR / "protocol.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"run_id": run_id, "created_unix": payload["created_unix"], "request": payload["request"],
                                 "explorative": True}, allow_nan=False) + "\n")
    return payload


class Handler(http.server.BaseHTTPRequestHandler):
    ui_dir: Path = DEFAULT_UI
    server_version = "MandalaMemoryLab/1"

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj):
        self._send(code, json.dumps(obj, allow_nan=False).encode(), "application/json; charset=utf-8")

    def do_GET(self):
        if self.path == "/api/preset":
            return self._json(200, {"config": CONFIG, "networks": NETWORKS, "interventions": INTERVENTIONS,
                                    "max_delay": MAX_DELAY, "max_runs": MAX_RUNS, "read_only": True})
        route = self.path.split("?", 1)[0]          # query strings (e.g. ?autostart) do not select files
        name = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/style.css": "style.css"}.get(route)
        if name is None:                               # fixed whitelist: no paths from the browser
            return self._json(404, {"error": "not found"})
        f = self.ui_dir / name
        if not f.is_file():
            return self._json(404, {"error": "ui file missing"})
        self._send(200, f.read_bytes(), mimetypes.guess_type(name)[0] or "text/plain")

    def do_POST(self):
        if self.path != "/api/run":
            return self._json(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n > 10_000:
                raise MemoryLabError("request too large")
            req = json.loads(self.rfile.read(n) or b"{}")
            return self._json(200, explore(req))
        except (MemoryLabError, ValueError) as e:
            return self._json(400, {"error": str(e)})

    def log_message(self, fmt, *args):  # keep the console quiet
        pass


def make_server(port: int = 8765, ui_dir: Path = DEFAULT_UI) -> http.server.ThreadingHTTPServer:
    Handler.ui_dir = Path(ui_dir)
    return http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--ui", type=Path, default=DEFAULT_UI)
    a = ap.parse_args(argv)
    srv = make_server(a.port, a.ui)
    print(f"Mandala memory lab on http://127.0.0.1:{a.port}/  (Ctrl+C to stop; explorative runs -> {EXPLORE_DIR})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
