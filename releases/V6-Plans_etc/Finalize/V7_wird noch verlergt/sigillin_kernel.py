import json
from pathlib import Path
from analysis.beta_meta_regression_v2 import run_beta_regression
from scripts.utils.audit import audit_delta_AIC
from scripts.sigillin_storage import store_sigillin

def mirror_machine(trilayer_data):
    # Platzhalter: Mirror-Machine verarbeitet Tri-Layer-Eintrag
    return trilayer_data  # Noch zu verfeinern mit Spiegelungslogik

def sigillin_kernel(trilayer_path):
    trilayer_data = json.loads(Path(trilayer_path).read_text())
    mirror_output = mirror_machine(trilayer_data)
    beta_fit = run_beta_regression(mirror_output)
    audit_result = audit_delta_AIC(beta_fit)

    if audit_result['pass']:
        store_sigillin(beta_fit, audit_result)
        print("[✔] Sigillin gespeichert: Schwelle überschritten.")
        return True
    else:
        print("[✘] Keine Speicherung: ΔAIC zu gering.")
        return False

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_trilayer.json"
    sigillin_kernel(path)
