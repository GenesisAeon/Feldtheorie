# Logistic resonance build choreography

.PHONY: install lint format test typecheck build batch planetary preset-guard release clean

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

clean:
	rm -rf .nox .pytest_cache build dist *.egg-info
