"""Runner for protocol KV-V5 (package V5). Deterministic; writes raw time series.

    python -m experiments.kosmische_vererbung.chem.run_v5 [--out DIR] [--force]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy

from .kernel import PRIMORDIAL, ChemState
from .rules import make_rule
from .zones import Zones

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol_v5.json"
DEFAULT_OUT = HERE / "runs" / "v5_mean_vs_distribution"
CODE = ("kernel.py", "zones.py", "rules.py", "run_v5.py")


def text_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def initial_zones(protocol: dict, init: str) -> Zones:
    spec = protocol["initial_states"][init]
    mass = protocol["zone_gas_mass"] * spec.get("mass_factor", 1)
    fr = protocol["primordial_mass_fractions"]
    zones = []
    for z in spec["zones"]:
        masses = {"H": fr["H"] * (1 - z) * mass, "He": fr["He"] * (1 - z) * mass, "O": z * mass}
        zones.append(ChemState.with_gas(masses, tag=PRIMORDIAL if z == 0 else "initial"))
    return Zones(zones)


def simulate(protocol: dict, rule_id: str, init: str, k: float, dt: float) -> dict:
    zones = initial_zones(protocol, init)
    rule = make_rule(protocol["rules"][rule_id])
    eps = protocol["star_formation"]["eps_per_myr"]
    n = len(zones.zones)
    rates = [[0.0 if i == j else k for i in range(n)] for j in range(n)]
    steps = round(protocol["duration_myr"] / dt)
    obs_every = round(protocol["observe_every_myr"] / dt)
    z_crit = protocol["observables"]["f0_z_crit"]
    initial_budget = zones.budget()
    series = {key: [] for key in ("t", "mean_Z", "zone_Z", "f0", "f_primordial_origin",
                                  "pop3_mass_formed", "synthesized_O", "gas_mass", "budget_rel_error")}
    pop3_mass = 0.0

    def observe(t):
        budget = zones.budget()
        scale = sum(abs(v) for v in initial_budget.values())
        series["t"].append(t)
        series["mean_Z"].append(zones.mean_metallicity())
        series["zone_Z"].append(zones.zone_metallicities())
        series["f0"].append(zones.f0(z_crit))
        series["f_primordial_origin"].append(zones.f_primordial_origin())
        series["pop3_mass_formed"].append(pop3_mass)
        series["synthesized_O"].append(sum(z.synthesized["O"] for z in zones.zones))
        series["gas_mass"].append(sum(zones.gas_masses()))
        series["budget_rel_error"].append(max(abs(budget[e] - initial_budget[e]) for e in budget) / scale)

    for step in range(steps):
        t = step * dt
        zones.advance_to(t)
        if step % obs_every == 0:
            observe(t)
        for zone, z in zip(zones.zones, zones.zone_metallicities()):
            model = rule(z)
            mass = eps * zone.gas_mass() * dt
            zone.form_stars(mass, model, t=t)
            if model.name == "pop3":
                pop3_mass += mass
        if n > 1 and k > 0:
            zones.exchange(rates, dt)
    zones.advance_to(steps * dt)
    observe(steps * dt)
    return series


def run(protocol: dict) -> dict:
    raw = {"protocol_id": protocol["protocol_id"], "runs": []}
    for dt in protocol["dt_myr"]:
        for rule_id in protocol["rules"]:
            for init in protocol["initial_states"]:
                ks = [0.0] if init == "C" else protocol["exchange_rates_per_myr"]
                for k in ks:
                    raw["runs"].append({"rule": rule_id, "init": init, "k": k, "dt": dt,
                                        "series": simulate(protocol, rule_id, init, k, dt)})
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
