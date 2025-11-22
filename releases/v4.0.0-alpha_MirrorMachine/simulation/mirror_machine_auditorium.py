"""Mirror Machine Auditorium

Meta-controller orchestrating sensor perception, chronology recall,
and hypothesis mutation for Sigillin MOR-FIT V4.0.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = BASE_DIR / "analysis" / "results" / "mirror_machine_state.json"

SENSOR_PATHS: Dict[str, List[Path]] = {
    "amoc": [
        BASE_DIR / "analysis" / "results" / "amoc_adapter_output.json",
        BASE_DIR / "data" / "derived" / "amoc_adapter_output.json",
    ],
    "wais": [
        BASE_DIR / "analysis" / "results" / "wais_adapter_output.json",
        BASE_DIR / "data" / "derived" / "wais_adapter_output.json",
    ],
    "coral": [
        BASE_DIR / "analysis" / "results" / "coral_adapter_output.json",
        BASE_DIR / "data" / "derived" / "coral_adapter_output.json",
    ],
}

SENSOR_WEIGHTS: Dict[str, float] = {"amoc": 0.34, "wais": 0.33, "coral": 0.33}
BROKEN_RAM_THRESHOLD = 30.0


@dataclass
class SensorPayload:
    name: str
    source_path: Path
    beta: float
    status: str
    timestamp: Optional[str]


def _find_first_existing(paths: List[Path]) -> Path:
    for path in paths:
        if path.exists():
            return path
    raise FileNotFoundError(f"No sensor output found in: {paths}")


def _extract_beta(payload: dict) -> Optional[float]:
    for key in ("beta_estimate", "beta_expected", "beta"):
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return float(value)

    for value in payload.values():
        if isinstance(value, dict):
            nested = _extract_beta(value)
            if nested is not None:
                return nested
    return None


def _extract_status(payload: dict) -> str:
    for key in ("status", "sensor_status"):
        value = payload.get(key)
        if isinstance(value, str):
            return value

    for value in payload.values():
        if isinstance(value, dict):
            nested = _extract_status(value)
            if nested:
                return nested
    return "unknown"


def load_sensor(sensor_key: str) -> SensorPayload:
    path = _find_first_existing(SENSOR_PATHS[sensor_key])
    payload = json.loads(path.read_text())

    beta = _extract_beta(payload)
    if beta is None:
        raise ValueError(f"No beta estimate found for sensor {sensor_key} in {path}")

    timestamp = payload.get("timestamp")
    status = _extract_status(payload)

    return SensorPayload(
        name=sensor_key,
        source_path=path,
        beta=beta,
        status=status,
        timestamp=timestamp,
    )


def compute_global_beta(sensors: List[SensorPayload]) -> float:
    total_weight = sum(SENSOR_WEIGHTS.get(sensor.name, 1.0) for sensor in sensors)
    weighted_sum = sum(
        sensor.beta * SENSOR_WEIGHTS.get(sensor.name, 1.0) for sensor in sensors
    )
    return weighted_sum / total_weight if total_weight else 0.0


def load_chronology_beta_curve(path: Path) -> List[dict]:
    chronology = json.loads(path.read_text())
    beta_history: List[dict] = []

    for section in chronology.get("sections", []):
        for version in section.get("versions", []):
            version_id = version.get("id", "unknown")
            text_fragments = [
                value for value in version.values() if isinstance(value, str)
            ]
            text = " ".join(text_fragments)

            matches = re.findall(r"β[≈=]?\s*([0-9]+(?:\.[0-9]+)?)", text)
            if not matches:
                matches = re.findall(r"beta[≈=]?\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)

            beta_value = float(matches[0]) if matches else None
            beta_history.append({"version": version_id, "beta": beta_value})

    return beta_history


def on_predicted_curve(beta_history: List[dict], current_beta: float) -> dict:
    recorded = [entry for entry in beta_history if entry["beta"] is not None]
    expected_beta = recorded[-1]["beta"] if recorded else None
    tolerance = 2.5

    alignment = False
    if expected_beta is not None:
        alignment = abs(current_beta - expected_beta) <= tolerance

    return {
        "expected_beta": expected_beta,
        "tolerance": tolerance,
        "aligned": alignment,
    }


def generate_mutation(beta_global: float, amoc_beta: float) -> dict:
    hypothesis = (
        "Hypothese: Wenn wir den AMOC-Fluss um 10% erhöhen, sinkt β_global um 2.0."
    )
    predicted_beta = max(beta_global - 2.0, 0.0)
    falsified = amoc_beta < 5.0

    return {
        "hypothesis": hypothesis,
        "predicted_beta": predicted_beta,
        "falsified": falsified,
    }


def verdict(beta_global: float, broken_ram: bool, sensors: List[SensorPayload]) -> dict:
    if broken_ram:
        status = "Collapsed"
    elif beta_global > 20.0 or any(sensor.status.lower() != "stable" for sensor in sensors):
        status = "Critical"
    else:
        status = "Stable"

    resonance = 0.0
    if sensors:
        mean_beta = sum(sensor.beta for sensor in sensors) / len(sensors)
        dispersion = sum(abs(sensor.beta - mean_beta) for sensor in sensors) / len(
            sensors
        )
        resonance = max(0.0, 1.0 - dispersion / (mean_beta + 1e-6))

    if status == "Collapsed":
        next_step = "Broken RAM Alarm aktiv: sofortige Systemsanierung einleiten."
    elif status == "Critical":
        next_step = "Falsifizierung von V3.0 abgeschlossen. Daten zeigen V4.0 Integrität."
    else:
        next_step = "System stabil. Monitoring der Sensoren fortsetzen."

    return {
        "system_status": status,
        "resonance": round(resonance, 3),
        "next_step": next_step,
    }


def run_auditorium(output_path: Path = DEFAULT_OUTPUT_PATH) -> dict:
    sensors = [load_sensor(key) for key in SENSOR_PATHS]
    beta_global = compute_global_beta(sensors)
    broken_ram = beta_global > BROKEN_RAM_THRESHOLD

    chronology_path = BASE_DIR / "seed" / "CHRONOLOGY.json"
    beta_history = load_chronology_beta_curve(chronology_path)
    chronology_alignment = on_predicted_curve(beta_history, beta_global)

    mutation = generate_mutation(beta_global, sensors[0].beta)
    verdict_payload = verdict(beta_global, broken_ram, sensors)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "beta_global": round(beta_global, 3),
        "broken_ram_alarm": broken_ram,
        "sensors": [
            {
                "name": sensor.name,
                "beta": sensor.beta,
                "status": sensor.status,
                "source": str(sensor.source_path),
                "timestamp": sensor.timestamp,
            }
            for sensor in sensors
        ],
        "chronology": {
            "beta_history": beta_history,
            "alignment": chronology_alignment,
        },
        "mutation": mutation,
        "verdict": verdict_payload,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2))
    return report


def main() -> None:
    report = run_auditorium()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
