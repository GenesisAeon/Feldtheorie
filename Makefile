# Logistic resonance build choreography

.PHONY: install lint format test typecheck build batch planetary preset-guard release dist-zenodo clean \
        install-ocf ingest-icon ingest-radar test-pipelines clean-cache run-meta-regression run-sonification

install:
	python -m pip install --upgrade pip
	python -m pip install -e .[dev]

lint:
	nox -s lint

format:
	nox -s format

test:
	nox -s tests

typecheck:
	nox -s typecheck

build:
	nox -s build

batch:
	utf-batch --config analysis/batch_configs/resonance_runs.json

planetary:
	utf-planetary-summary --output analysis/results/planetary_tipping_elements.json

preset-guard:
	utf-preset-guard

release: lint test typecheck build
	@echo "ΔAIC guards aligned; release bundle ready."

VERSION ?= $(shell python scripts/zenodo_version.py)
DIST_ZENODO_DIR = dist/zenodo
DIST_ZENODO_ARCHIVE = UTAC-v$(VERSION)-zenodo.zip
DIST_ZENODO_METADATA = zenodo_record_v$(VERSION).json

dist-zenodo:
ifndef SKIP_RELEASE_CHECKS
	$(MAKE) release
endif
	mkdir -p $(DIST_ZENODO_DIR)
	git archive --format=zip --output $(DIST_ZENODO_DIR)/$(DIST_ZENODO_ARCHIVE) HEAD
	python scripts/prepare_zenodo_metadata.py --version $(VERSION) --output $(DIST_ZENODO_DIR)/$(DIST_ZENODO_METADATA)
	@echo "Zenodo archive ready → $(DIST_ZENODO_DIR)/$(DIST_ZENODO_ARCHIVE)"

clean:
	rm -rf .nox .pytest_cache build dist *.egg-info

# ============================================================================
# OCF Data Pipelines (added 2025-11-12)
# Portions inspired by Open Climate Fix (MIT). See ACKNOWLEDGEMENTS.md.
# ============================================================================

install-ocf:
	@echo "Installing OCF pipeline dependencies..."
	python3 -m pip install --break-system-packages -r requirements-ocf.txt
	@echo "✅ OCF dependencies installed"

ICON_EU_URL ?= https://huggingface.co/datasets/openclimatefix/dwd-icon-eu/resolve/main/icon_eu.zarr
ICON_EU_OUT ?= ./data/fieldcube/icon_eu.zarr

ingest-icon:
	@echo "Ingesting ICON-EU → FieldCube..."
	@python3 -c 'from pipelines.ocf_sources.icon_eu import load_icon_eu_zarr; from pipelines.transform.standardize import to_fieldcube; from pipelines.sinks.zarr_store import write_zarr; URL="$(ICON_EU_URL)"; OUT="$(ICON_EU_OUT)"; REN={"t_2m":"t2m","u_10m":"u10","v_10m":"v10","total_precipitation":"tp","ssrd":"ssrd"}; ds=load_icon_eu_zarr(URL,rename_map=REN); fc=to_fieldcube(ds,global_attrs={"source":"ICON-EU via OCF"}); write_zarr(fc,OUT); print(f"✅ ICON-EU → {OUT}")'

RADAR_URL ?= s3://my-bucket/radar/nimrod.zarr
RADAR_OUT ?= ./data/fieldcube/radar.zarr

ingest-radar:
	@echo "Ingesting Radar → FieldCube..."
	@python3 -c 'from pipelines.ocf_sources.nimrod import load_radar_zarr; from pipelines.transform.standardize import to_fieldcube; from pipelines.sinks.zarr_store import write_zarr; URL="$(RADAR_URL)"; OUT="$(RADAR_OUT)"; REN={"rainrate":"rr","reflectivity":"dbz"}; ds=load_radar_zarr(URL,rename_map=REN); fc=to_fieldcube(ds,global_attrs={"source":"Radar"}); write_zarr(fc,OUT); print(f"✅ Radar → {OUT}")'

test-pipelines:
	@echo "Testing OCF pipeline modules..."
	@python3 -c "from pipelines.ocf_sources.icon_eu import load_icon_eu_zarr; print('✅ icon_eu')"
	@python3 -c "from pipelines.ocf_sources.nimrod import load_radar_zarr; print('✅ nimrod')"
	@python3 -c "from pipelines.transform.standardize import to_fieldcube; print('✅ standardize')"
	@python3 -c "from pipelines.sinks.zarr_store import write_zarr, read_zarr; print('✅ zarr_store')"
	@echo "✅ All pipeline modules OK"

run-meta-regression:
	@echo "Running UTAC meta-regression..."
	python3 analysis/beta_meta_regression_v2_field_types.py
	@echo "✅ Meta-regression complete"

run-sonification:
	@echo "Generating UTAC sonifications..."
	python3 -m sonification.utac_sonification --preset llm_emergence --output-dir sonification/output
	@echo "✅ Sonifications generated"

clean-cache:
	@echo "Cleaning Zarr/Dask cache..."
	find . -type d -name ".zarr" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dask-worker-space" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cache cleaned"

# ============================================================================
# RG Phase 2 Validation Pipeline (added 2025-11-13)
# ============================================================================

PYTHON ?= python3

validate:
	@echo "🔬 Running RG Phase 2 Validation..."
	@RG_SIM_ENTRYPOINT="scripts.stubs.rg_sim_stub:simulate" \
	$(PYTHON) scripts/validate_phase2.py --seeds 0 1 2 3 4 5 6 7 8 9 --lattice 64 128 256 --noise gaussian laplace poisson --J_over_T 0.5 1.0 1.5 2.0
	@echo "✅ Validation complete"

aggregate:
	@echo "📊 Aggregating validation results..."
	@$(PYTHON) scripts/aggregate_validation.py
	@echo "✅ Aggregation complete"

plots:
	@echo "📈 Generating validation plots..."
	@$(PYTHON) - <<'PY'
from analysis.plots.rg_flow_plots import plot_overview
plot_overview(save="analysis/results/plots")
PY
	@echo "✅ Plots saved to analysis/results/plots/"

reproduce: validate aggregate plots
	@echo "🎉 Reproduce complete: analysis/results/*"
