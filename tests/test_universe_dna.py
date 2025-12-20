import numpy as np

from simulation.v4_stellar_forge import physics_engine
from simulation.v4_stellar_forge.universe_dna import UniverseDNA


def test_seed_token_round_trip_uses_hashed_seed():
    dna = UniverseDNA(gravity_const=0.12, fusion_threshold=0.7, entropy_rate=0.003)

    token = dna.to_seed_token()
    decoded, seed = UniverseDNA.from_seed_token(token)

    assert decoded == dna
    assert seed == UniverseDNA._hash_seed(token)


def test_numeric_seed_bypasses_json_parsing():
    dna, seed = UniverseDNA.from_seed_token("1234")

    assert dna is None
    assert seed == 1234


def test_invalid_json_hashes_to_seed():
    token = "<not-json>"

    dna, seed = UniverseDNA.from_seed_token(token)

    assert dna is None
    assert seed == UniverseDNA._hash_seed(token)


def test_mutate_jitters_constants_within_scale():
    dna = UniverseDNA(gravity_const=0.1, fusion_threshold=0.5, entropy_rate=0.002)
    rng = np.random.default_rng(7)

    mutated = dna.mutate(rng=rng)

    assert mutated != dna
    assert 0.95 <= mutated.gravity_const / dna.gravity_const <= 1.05
    assert 0.95 <= mutated.fusion_threshold / dna.fusion_threshold <= 1.05
    assert 0.95 <= mutated.entropy_rate / dna.entropy_rate <= 1.05


def test_apply_universe_dna_overrides_global_constants():
    original = (
        physics_engine.GRAVITATIONAL_CONSTANT,
        physics_engine.FUSION_DISTANCE,
        physics_engine.FUSION_THRESHOLD,
        physics_engine.HAWKING_DECAY_RATE,
    )
    dna = UniverseDNA(gravity_const=0.2, fusion_threshold=1.1, entropy_rate=0.004)

    try:
        physics_engine.apply_universe_dna(dna)

        assert physics_engine.GRAVITATIONAL_CONSTANT == dna.gravity_const
        assert physics_engine.FUSION_DISTANCE == dna.fusion_threshold
        assert physics_engine.FUSION_THRESHOLD == dna.fusion_threshold
        assert physics_engine.HAWKING_DECAY_RATE == dna.entropy_rate
    finally:
        (
            physics_engine.GRAVITATIONAL_CONSTANT,
            physics_engine.FUSION_DISTANCE,
            physics_engine.FUSION_THRESHOLD,
            physics_engine.HAWKING_DECAY_RATE,
        ) = original
