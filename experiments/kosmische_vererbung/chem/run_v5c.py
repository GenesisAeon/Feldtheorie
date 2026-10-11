"""Runner for protocol KV-V5c (resolution study of KV-V5). Deterministic.

    python -m experiments.kosmische_vererbung.chem.run_v5c [--out DIR] [--force]

Two schemes over the same model as KV-V5 (kernel, zones and rules unchanged):

* ``grid``  exactly the KV-V5 step: at every grid time t_n star formation
  eps*M_gas*dt with the rule evaluated at Z(t_n), then exchange over dt.
* ``event`` the same lumping, but every step is split at breakpoints:
  (a) star deaths inside the step, (b) the time at which a zone with
  Z < z_crit reaches z_crit through exchange. (b) is found by bisection on the
  exact exchange solution (between breakpoints only exchange changes Z: star
  formation takes gas at its own composition and no star dies). The returned
  breakpoint is the upper end of the bracket, so the zone is at or above
  z_crit afterwards.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from .kernel import METALS
from .rules import make_rule
from .run_v5 import initial_zones
from .zones import transfer_matrix

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol_v5c.json"
DEFAULT_OUT = HERE / "runs" / "v5c_resolution"
CODE = ("kernel.py", "zones.py", "rules.py", "run_v5.py", "run_v5c.py")
SCHEMES = ("grid", "event")


def text_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _metal_and_gas(zones):
    metals = np.array([sum(z.gas_masses()[e] for e in METALS) for z in zones.zones], dtype=float)
    gas = np.array(zones.gas_masses(), dtype=float)
    return metals, gas


def crossing_time(zones, rates, z_crit, horizon, xtol):
    """Earliest tau in (0, horizon] at which a zone below z_crit reaches it
    through exchange alone; ``None`` if none does. Returns the bracket's upper
    end, so Z >= z_crit holds at the returned time."""

    metals, gas = _metal_and_gas(zones)
    below = [j for j in range(len(gas)) if gas[j] > 0 and metals[j] / gas[j] < z_crit]
    if not below or horizon <= 0:
        return None

    def z(tau, j):
        P = transfer_matrix(rates, tau)
        return (P @ metals)[j] / (P @ gas)[j]

    best = None
    for j in below:
        if z(horizon, j) < z_crit:
            continue
        lo, hi = 0.0, horizon
        while hi - lo > xtol:
            mid = 0.5 * (lo + hi)
            if z(mid, j) >= z_crit:
                hi = mid
            else:
                lo = mid
        best = hi if best is None else min(best, hi)
    return best


def simulate(protocol: dict, rule_id: str, init: str, k: float, dt: float, scheme: str) -> dict:
    if scheme not in SCHEMES:
        raise ValueError(f"unknown scheme {scheme!r}")
    zones = initial_zones(protocol, init)
    rule = make_rule(protocol["rules"][rule_id])
    eps = protocol["star_formation"]["eps_per_myr"]
    n = len(zones.zones)
    rates = [[0.0 if i == j else k for i in range(n)] for j in range(n)]
    exchange = n > 1 and k > 0
    steps = round(protocol["duration_myr"] / dt)
    obs_every = round(protocol["observe_every_myr"] / dt)
    z_crit = protocol["rules"]["P3"]["z_crit"]
    xtol = protocol["event_scheme"]["xtol_myr"]
    max_splits = protocol["event_scheme"]["max_splits_per_step"]
    initial_budget = zones.budget()
    scale = sum(abs(v) for v in initial_budget.values())
    series = {key: [] for key in ("t", "mean_Z", "f0", "pop3_mass_formed", "budget_rel_error")}
    pop3_mass = 0.0
    splits = 0

    def observe(t):
        budget = zones.budget()
        series["t"].append(t)
        series["mean_Z"].append(zones.mean_metallicity())
        series["f0"].append(zones.f0(protocol["observables"]["f0_z_crit"]))
        series["pop3_mass_formed"].append(pop3_mass)
        series["budget_rel_error"].append(max(abs(budget[e] - initial_budget[e]) for e in budget) / scale)

    def form(t, length):
        nonlocal pop3_mass
        for zone, z in zip(zones.zones, zones.zone_metallicities()):
            model = rule(z)
            mass = eps * zone.gas_mass() * length
            zone.form_stars(mass, model, t=t)
            if model.name == "pop3":
                pop3_mass += mass

    for step in range(steps):
        t0 = step * dt
        t_end = (step + 1) * dt
        zones.advance_to(t0)
        if step % obs_every == 0:
            observe(t0)
        if scheme == "grid":
            form(t0, dt)
            if exchange:
                zones.exchange(rates, dt)
            continue
        t = t0
        local = 0
        while t < t_end:
            deaths = [s.t_death for z in zones.zones for s in z.stars if t < s.t_death < t_end]
            t_b = min(deaths) if deaths else t_end
            if exchange and rule_id == "P3":
                tau = crossing_time(zones, rates, z_crit, t_b - t, xtol)
                if tau is not None and t + tau < t_b:
                    t_b = t + tau
            form(t, t_b - t)
            if exchange:
                zones.exchange(rates, t_b - t)
            zones.advance_to(t_b)
            if t_b < t_end:
                local += 1
                splits += 1
                if local > max_splits:
                    raise RuntimeError(f"more than {max_splits} event splits in step {step}")
            t = t_b
    zones.advance_to(steps * dt)
    observe(steps * dt)
    series["event_splits"] = splits
    return series


def run(protocol: dict) -> dict:
    raw = {"protocol_id": protocol["protocol_id"], "runs": []}
    for scheme in SCHEMES:
        for dt in protocol["dt_myr"]:
            for rule_id in protocol["rules"]:
                for init in ("A", "B"):
                    for k in protocol["exchange_rates_per_myr"]:
                        entry = {"scheme": scheme, "rule": rule_id, "init": init, "k": k, "dt": dt}
                        try:
                            entry["series"] = simulate(protocol, rule_id, init, k, dt, scheme)
                            entry["state"] = "completed"
                        except Exception as exc:  # recorded, evaluated as not_evaluated
                            entry["state"] = "failed"
                            entry["error"] = f"{type(exc).__name__}: {exc}"
                        raw["runs"].append(entry)
    raw["provenance"] = {
        "protocol_sha256": text_sha256(PROTOCOL),
        "code_sha256": {name: text_sha256(HERE / name) for name in CODE},
        "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
    }
    return raw


def main(argv=None) -> Path:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    target = args.out / "raw.json"
    if target.exists() and not args.force:
        raise SystemExit(f"{target} exists; refusing to overwrite (use --force)")
    raw = run(json.loads(PROTOCOL.read_text(encoding="utf-8")))
    args.out.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(raw, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {target}")
    return target


if __name__ == "__main__":
    main()
