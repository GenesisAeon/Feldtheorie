# Logistic resonance build choreography

.PHONY: install lint format test typecheck build batch planetary preset-guard release dist-zenodo clean

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
