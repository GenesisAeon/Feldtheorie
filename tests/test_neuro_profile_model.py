import importlib.util
import sys
import types
from pathlib import Path

import numpy as np
import pytest


def load_neuroprofile_module():
    base_dir = Path("experiments/Phaethon_Geminiden_Bennu/NeuroProfile/code").resolve()
    package_name = "neuroprofile_code"
    package = types.ModuleType(package_name)
    package.__path__ = [str(base_dir)]
    sys.modules[package_name] = package

    module_path = base_dir / "neuro_profile_model.py"
    spec = importlib.util.spec_from_file_location(f"{package_name}.neuro_profile_model", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_consent_required():
    module = load_neuroprofile_module()
    model = module.NeuroProfileModel()
    with pytest.raises(PermissionError):
        model.analyze([0.0, 1.0, 0.5])


def test_analysis_outputs():
    module = load_neuroprofile_module()
    model = module.NeuroProfileModel()
    rng = np.random.default_rng(1)
    series = rng.normal(0.0, 1.0, 256)
    result = model.analyze(
        series, consent_granted=True, consent_token="unit-test-token", subject_id="unit-test"
    )

    assert result.beta_ci[0] <= result.beta_estimate.beta <= result.beta_ci[1]
    assert result.sigma_phi_ci[0] <= result.sigma_phi_proxy <= result.sigma_phi_ci[1]
    assert result.null_models.best_model in result.null_models.aic
    assert result.consent.granted is True
    assert result.consent.anonymized_subject
