"""Export the KV-V5 time series for the SCF adapter (KV3). Reads only raw.json.

    python -m experiments.kosmische_vererbung.chem.export_v5_timeseries [--run DIR]

Writes timeseries.json: one entry per rule x initial state x exchange rate at
the primary dt, with t [Myr], mean_Z, f0 (zones with Z < f0_z_crit),
f_primordial_origin, zone_Z and gas_mass [M_sun]. The fine-dt runs are left
out on purpose; they only serve the resolution check (D4).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol_v5.json"
DEFAULT_RUN = HERE / "runs" / "v5_mean_vs_distribution"
FIELDS = ("t", "mean_Z", "f0", "f_primordial_origin", "zone_Z", "gas_mass")


def export(protocol: dict, raw: dict) -> dict:
    dt = protocol["primary_dt_myr"]
    return {
        "protocol_id": protocol["protocol_id"],
        "units": protocol["units"],
        "f0_definition": protocol["observables"]["f0"],
        "f0_z_crit": protocol["observables"]["f0_z_crit"],
        "f_primordial_origin_definition": protocol["observables"]["f_primordial_origin"],
        "dt_myr": dt,
        "status": "synthetic_only",
        "raw_protocol_sha256": raw["provenance"]["protocol_sha256"],
        "series": [
            {"rule": r["rule"], "init": r["init"], "k_per_myr": r["k"], **{f: r["series"][f] for f in FIELDS}}
            for r in raw["runs"] if r["dt"] == dt
        ],
    }


def main(argv=None) -> Path:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args(argv)
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    out = export(protocol, json.loads((args.run / "raw.json").read_text(encoding="utf-8")))
    target = args.run / "timeseries.json"
    target.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {target}")
    return target


if __name__ == "__main__":
    main()
