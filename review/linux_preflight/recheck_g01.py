"""Execute Claude's own reference functions and compare every published field.

This is a replay of the independent implementation, not a third independent
implementation. Outputs are exclusive; no published review file is changed.
"""

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import runpy


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "review/g01_independent/independent_recompute.py"
EXPERIMENT = ROOT / "experiments/geometric_waste_v1"


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def execute(output):
    ref = runpy.run_path(str(REFERENCE))
    states = list(ref["enumerate_states"]())
    check(len(states) == 65536 and len(set(states)) == 65536, "Wrong enumeration")
    check([ref["state_id"](b) for b in states] == list(range(65536)), "Wrong state order")
    half = [b for b in states if ref["occupancy_of"](b) == 8]
    check(len(half) == 12870, "Wrong fixed-density count")
    published = json.loads((EXPERIMENT / "runs/calibration_v1/results.json").read_text())
    independent = json.loads((REFERENCE.parent / "independent_results.json").read_text())
    recomputed, differences = {}, []
    class_records = {}
    for ensemble, sample in (("uniform_all", states), ("uniform_density_half", half)):
        blocks = [ref["block_label"](b) for b in sample]
        boundary = [ref["boundary_length_of"](b) for b in sample]
        labels = {"identity":[(i,) for i in range(len(sample))],
                  "occupancy":[(sum(b),) for b in sample], "block_counts":blocks,
                  "block_counts_boundary":[block+(length,) for block,length in zip(blocks,boundary)]}
        for seed in (11,23,47):
            shuffled = ref["scrambled_permutation"](boundary, seed)
            labels[f"block_counts_scrambled_{seed}"] = [block+(v,) for block,v in zip(blocks,shuffled)]
        recomputed[ensemble] = {}
        for observer, observation in labels.items():
            values = ref["conditional_entropy_and_error"](sample, observation)
            recomputed[ensemble][observer] = values
            for field, value in values.items():
                for source, expected in (("published", published), ("independent", independent)):
                    wanted = expected["ensembles"][ensemble][observer][field]
                    delta = abs(value - wanted)
                    check(delta <= 1e-12, f"{source}/{ensemble}/{observer}/{field}: {delta}")
                    differences.append(delta)
            if ensemble == "uniform_density_half" and observer in ("block_counts","block_counts_boundary"):
                grouped = defaultdict(list)
                for state,label in zip(sample,observation):
                    grouped[label].append(state)
                for label,members in grouped.items():
                    error = sum(min(sum(b[k] for b in members), len(members)-sum(b[k] for b in members))
                                for k in range(16))/(len(members)*16)
                    class_records[observer,":".join(map(str,label))] = (len(members),math.log2(len(members)),error)
    rows = list(csv.DictReader((EXPERIMENT / "runs/calibration_v1/observation_classes.csv").open()))
    check(len(rows) == len(class_records) == 401, "Wrong number of class records")
    for row in rows:
        wanted = class_records[row["observer"],row["label"]]
        got = (int(row["microstates"]),float(row["conditional_entropy_bits"]),float(row["bayes_cell_error_fraction"]))
        check(all(abs(a-b) <= 1e-12 for a,b in zip(got,wanted)), "Class record differs")
    sanity = ref["sanity_checks"](states)
    for key,value in sanity.items():
        if isinstance(value,bool):
            check(value, "Sanity check failed: "+key)
    for key,value in (("boundary_empty",0),("boundary_single_cell",4),
                      ("boundary_vertical_half_plane",8),("boundary_checkerboard",32)):
        check(sanity[key] == value, "Wrong boundary fixture: "+key)
    fair = ref["block_independent_fair_binary_check"]()
    check(fair["matches_within_1e-9"], "Analytic block check failed")
    # The original reference's rotation-named check is a row translation only.
    # Supplement it with genuine quarter-turns and translations on every state.
    for bits in states:
        boundary = ref["boundary_length_of"](bits)
        rotated = tuple(bits[(3-c)*4+r] for r in range(4) for c in range(4))
        translated = tuple(bits[((r-1)%4)*4+(c-1)%4] for r in range(4) for c in range(4))
        check(ref["boundary_length_of"](rotated) == boundary, "Rotation failed")
        check(ref["boundary_length_of"](translated) == boundary, "Translation failed")
    result = {"status":"passed", "scope":"Linux replay of Claude's independent reference",
              "reference_sha256":hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
              "python":platform.python_version(), "numpy":ref["np"].__version__,
              "max_absolute_numeric_difference":max(differences),
              "observer_results_checked":14, "numeric_comparisons":len(differences),
              "class_records_checked":len(rows), "rotation_and_translation_states_checked":len(states),
              "sanity_checks":sanity, "fair_block_check":fair, "ensembles":recomputed}
    with output.open("x") as handle:
        json.dump(result,handle,indent=2)
        handle.write("\n")
    print(json.dumps({key:result[key] for key in ("status","max_absolute_numeric_difference",
                     "observer_results_checked","class_records_checked","rotation_and_translation_states_checked")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    execute(parser.parse_args().output)
