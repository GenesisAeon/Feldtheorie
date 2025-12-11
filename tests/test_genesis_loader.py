from pathlib import Path

import pytest
from simulation.genesis_cube import GenesisCubeConfig
from simulation.genesis_loader import (
    GenesisLoader,
    GenesisPreset,
    index_presets,
    load_beta_presets,
    resolve_preset,
)


def test_load_beta_presets_filters_invalid_rows(tmp_path: Path) -> None:
    header = (
        "domain,beta,beta_ci_lower,beta_ci_upper,beta_ci_width,theta,r_squared,delta_aic,source"
    )
    rows = [
        "climate_amoc,4.02,3.5,4.55,1.04,0.175,0.987,29.4,Global Tipping Points 2025",
        "urban_heat,16.27,15.4,16.99,1.55,0.307,0.9994,64.6,",
        "neuro_brain,5.1,4.9,5.3,0.4,,0.97,12.0,Brain Study",
        # Missing columns (simulates line wrap)
        "forest_fire_percolation,9.48,8.85,10.15,1.3,0.59,0.968",
        # Should be skipped because domain is numeric
        "12345,not_a_beta,0,0,0,0,0,0,Bad row",
    ]

    csv_path = tmp_path / "beta.csv"
    csv_path.write_text("\n".join([header, *rows]))

    presets = load_beta_presets(csv_path)
    names = {preset.name for preset in presets}

    assert "climate_amoc" in names
    assert "urban_heat" in names
    assert "neuro_brain" in names
    assert "forest_fire_percolation" in names
    assert all(preset.beta > 0 for preset in presets)


def test_resolve_preset_is_case_and_separator_insensitive() -> None:
    presets = [
        GenesisPreset(name="climate_amoc", beta=4.02, theta=0.175),
        GenesisPreset(name="LLM_emergent", beta=3.47, theta=9.87),
    ]
    preset_index = index_presets(presets)

    resolved = resolve_preset("CLIMATE-AMOC", preset_index)
    assert resolved.beta == pytest.approx(4.02)
    assert resolved.theta == pytest.approx(0.175)

    with pytest.raises(KeyError):
        resolve_preset("unknown_preset", preset_index)


def test_apply_to_config_overrides_beta_and_theta() -> None:
    base = GenesisCubeConfig(beta=2.0, theta=0.1, damping=0.05)
    preset = GenesisPreset(name="amoc", beta=4.0, theta=0.2)

    updated = preset.apply_to_config(base)

    assert updated.beta == pytest.approx(4.0)
    assert updated.theta == pytest.approx(0.2)
    # other fields remain untouched
    assert updated.damping == pytest.approx(0.05)


def test_list_domains_loads_presets_when_empty(tmp_path: Path) -> None:
    csv_path = tmp_path / "beta.csv"
    csv_path.write_text(
        "\n".join(
            [
                "domain,beta,beta_ci_lower,beta_ci_upper,beta_ci_width,theta,r_squared,delta_aic,source",
                "information,4.2,3.9,4.5,0.6,0.12,0.98,12.1,lab",
                "climate,10.1,9.8,10.4,0.6,,0.99,42.0,field",
            ]
        )
    )

    loader = GenesisLoader(csv_path)
    assert loader.presets == {}

    domains = loader.list_domains()

    assert domains == ["climate", "information"]
    # ensure presets were cached after the lazy load
    assert len(loader.presets) == 2
