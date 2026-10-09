import json
from pathlib import Path
R = Path("D:/mandala/mandala-memory-results/lantern/runs")
a = json.loads((R / "lr6-acceptance-20261009T165010Z/release_report.json").read_text(encoding="utf-8"))
b = json.loads((R / "lr6-acceptance-20261009T192821Z/release_report.json").read_text(encoding="utf-8"))


def cells(r):
    def f(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "cells" and isinstance(v, dict) and all(isinstance(x, dict) and "holm_p" in x for x in v.values()):
                    return v
                x = f(v)
                if x:
                    return x
    return f(r)


ca, cb = cells(a), cells(b)
print("alarm cells identical (G, p, holm_p):", all(ca[k] == cb[k] for k in ca), "min holm", min(x["holm_p"] for x in cb.values()))
# scores of all records identical?
diff = 0
devs = []
for rec in sorted((R / "lr6-acceptance-20261009T192821Z/cells").glob("*/record.json")):
    r3 = json.loads(rec.read_text(encoding="utf-8"))
    r2 = json.loads((R / "lr6-acceptance-20261009T165010Z/cells" / rec.parent.name / "record.json").read_text(encoding="utf-8"))
    if r3["scores"] != r2["scores"] or r3["model"]["model_identity"] != r2["model"]["model_identity"]:
        diff += 1
    if "null" in r3:
        devs.append(r3["null"]["refit_path_check"]["abs_deviation"])
        assert r3["null"]["arrays"] == r2["null"]["arrays"]
print("records with different scores/model:", diff, "of 392; null arrays identical to run 2; max refit-path deviation", max(devs), "n", len(devs))
