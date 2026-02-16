# Logistic resonance build choreography

.PHONY: install lint format test typecheck build batch planetary preset-guard release dist-zenodo clean \
        install-ocf ingest-icon ingest-radar test-pipelines clean-cache run-meta-regression run-sonification \
        validate aggregate plots reproduce validate-trilayer crep-guard crep-guard-strict analyze-aletheia-phase4 \
        docs-index docs-index-sync test-v9 doctor

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

docs-index:
	@echo "Refreshing docs index parity snapshot..."
	@python scripts/archive_sigillin.py --recount --recount-targets docs --dry-run
	@echo "✅ docs-index check complete"

docs-index-sync:
	@echo "Syncing docs-index entries to match filesystem..."
	@python scripts/archive_sigillin.py --sync-entries
	@python scripts/archive_sigillin.py --recount --recount-targets docs
	@echo "✅ docs-index sync complete"

test-v9:
	@echo "Running v9_alpha tests..."
	@cd v9_alpha && python -m pytest -q
	@echo "✅ v9_alpha tests complete"

release: lint test typecheck crep-guard build
	@echo "ΔAIC guards aligned; CREP/τ* safety verified; release bundle ready."

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

analyze-aletheia-phase4:
	@echo "🧪 Analyzing Project Aletheia Phase 4 (Affection Experiment)..."
	python3 scripts/analyze_aletheia_phase4.py
	@echo "✅ Phase 4 analysis complete → analysis/results/phase4_affection/"

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

# ============================================================================
# V6 TriLayer Validation (added 2025-11-24)
# Validates consistency between YAML/JSON/MD ToDo representations
# ============================================================================

validate-trilayer:
	@echo "🔍 Validating TriLayer consistency (YAML/JSON/MD)..."
	@$(PYTHON) scripts/validate_trilayer.py
	@echo "✅ validate-trilayer complete"

crep-guard:
	@echo "🛡️  Running CREP/τ* Safety Guard (Type-VI Trilayer)..."
	@$(PYTHON) -m tools.crep_guard --check-type6-trilayer --threshold 0.7 --tau-default 0.1
	@echo "✅ crep-guard complete"

crep-guard-strict:
	@echo "🛡️  Running CREP/τ* Safety Guard (strict mode)..."
	@PYTHONWARNINGS=error $(PYTHON) -m tools.crep_guard --check-type6-trilayer --threshold 0.7 --tau-default 0.1
	@echo "✅ crep-guard-strict complete"

validate-type6:
	@echo "🔍 Validating Type-VI governance artifacts..."
	@$(PYTHON) -m tools.crep_guard --check-type6-trilayer --threshold 0.7 --tau-default 0.1
	@echo "✅ Type-VI validation complete (CREP threshold 0.7, τ*=0.1·|Θ-R|)"

# ============================================================================
# Developer Health Check
# ============================================================================

doctor:
	@echo "🩺 Feldtheorie Environment Doctor"
	@echo "================================="
	@echo ""
	@echo "1. Python environment"
	@python3 --version
	@python -c "import feldtheorie; print('   feldtheorie package: installed')" 2>/dev/null || python3 -c "import feldtheorie; print('   feldtheorie package: installed')" 2>/dev/null || echo "   ⚠  feldtheorie package: NOT installed (run make install)"
	@echo ""
	@echo "2. Core dependencies"
	@python3 -c "import numpy; print(f'   numpy {numpy.__version__}')" 2>/dev/null || echo "   ❌ numpy: MISSING"
	@python3 -c "import scipy; print(f'   scipy {scipy.__version__}')" 2>/dev/null || echo "   ❌ scipy: MISSING"
	@python3 -c "import pandas; print(f'   pandas {pandas.__version__}')" 2>/dev/null || echo "   ❌ pandas: MISSING"
	@python3 -c "import yaml; print(f'   pyyaml {yaml.__version__}')" 2>/dev/null || echo "   ❌ pyyaml: MISSING"
	@echo ""
	@echo "3. Optional dependencies"
	@python3 -c "import fastapi; print(f'   fastapi {fastapi.__version__}')" 2>/dev/null || echo "   ⚠  fastapi: not installed (pip install -e \".[api]\")"
	@python3 -c "import streamlit; print(f'   streamlit {streamlit.__version__}')" 2>/dev/null || echo "   ⚠  streamlit: not installed"
	@echo ""
	@echo "4. Test collection"
	@python3 -m pytest --collect-only -q 2>&1 | tail -1
	@echo ""
	@echo "5. Docs-index parity"
	@python3 scripts/archive_sigillin.py --recount --recount-targets docs --dry-run 2>&1 | grep -E "Filesystem|Listed|✅"
	@echo ""
	@echo "6. Trilayer sync"
	@python3 scripts/sigillin_sync.py report 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); m=d['meta']; print(f'   Trilayers: {m[\"counts\"][\"total\"]}, gaps: {m[\"counts\"][\"with_gaps\"]}')"
	@echo ""
	@echo "🩺 Doctor complete."
