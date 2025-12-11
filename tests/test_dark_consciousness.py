import pytest
from simulation.genesis_cube import GenesisCube, GenesisCubeConfig


def test_dark_consciousness_wireframe_mode():
    config = GenesisCubeConfig(photon_coupling=0.1)
    cube = GenesisCube(config=config)

    visibility = cube.calculate_visibility(base_visibility=1.0)

    assert pytest.approx(0.1) == visibility
    assert cube.is_dark_consciousness is True
    assert cube.get_render_mode() == "WIREFRAME"
