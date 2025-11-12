"""
Airflow DAG: ICON-EU → FieldCube → Zarr

Portions inspired by Open Climate Fix (MIT). Use with attribution.
Original code © Open Climate Fix. See ACKNOWLEDGEMENTS.md for full attribution.

Activation:
- Set AIRFLOW_HOME environment variable
- Install requirements-ocf.txt (with apache-airflow)
- Place DAG in $AIRFLOW_HOME/dags/
- Start Airflow webserver & scheduler

Note: For simple runs, a CLI script without Airflow suffices.
"""
from __future__ import annotations
from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator

# Add repo root to PYTHONPATH (if outside Airflow environment)
REPO_ROOT = os.environ.get("FELDTHEORIE_REPO_ROOT")
if REPO_ROOT and REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from pipelines.ocf_sources.icon_eu import load_icon_eu_zarr
from pipelines.transform.standardize import to_fieldcube
from pipelines.sinks.zarr_store import write_zarr

# Configuration from environment
SRC = os.environ.get(
    "ICON_EU_ZARR",
    "https://huggingface.co/datasets/openclimatefix/dwd-icon-eu/resolve/main/icon_eu.zarr"
)
DST = os.environ.get("ICON_EU_OUT", "/data/fieldcube/icon_eu.zarr")

RENAME = {
    "t_2m": "t2m",
    "u_10m": "u10",
    "v_10m": "v10",
    "total_precipitation": "tp",
    "ssrd": "ssrd",
}


def run_ingest():
    """Execute ICON-EU → FieldCube → Zarr pipeline."""
    ds = load_icon_eu_zarr(SRC, rename_map=RENAME)
    fc = to_fieldcube(ds, global_attrs={
        "source": "ICON-EU via OCF",
        "institution": "GenesisAeon/Feldtheorie",
    })
    write_zarr(fc, DST)


with DAG(
    dag_id="feldtheorie_icon_ingest",
    description="ICON-EU → FieldCube → Zarr",
    default_args={"depends_on_past": False},
    schedule=timedelta(hours=6),  # Run every 6 hours (00Z, 06Z, 12Z, 18Z)
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["feldtheorie", "ocf", "nwp"],
) as dag:

    ingest = PythonOperator(
        task_id="ingest_icon_eu",
        python_callable=run_ingest,
    )
