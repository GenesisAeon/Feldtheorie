from models.coherence_term import mandala_coherence
from models.recursive_threshold import CascadeState, PotenzialKaskade


def test_potenzialkaskade_step_updates_theta_and_beta() -> None:
    cascade = PotenzialKaskade(theta=0.4, beta=4.2, cascade_gain=0.5, condition_relaxation=0.1)
    coherence = mandala_coherence([0.1, 0.5, 0.9], [0.1, 0.45, 0.85])

    state = cascade.step(potential=0.9, coherence=coherence, dt=0.5)

    assert isinstance(state, CascadeState)
    assert state.theta > 0.4
    assert state.beta > 4.2
    assert 0.0 <= state.gate <= 1.0
    assert state.zeta <= cascade.zeta_closed
    assert cascade.history[-1] == state


def test_potenzialkaskade_run_handles_sequences() -> None:
    cascade = PotenzialKaskade(theta=0.3, beta=4.0)
    potentials = [0.2, 0.4, 0.8]
    coherences = [0.0, 0.3, 0.6]

    history = cascade.run(potentials, coherences)

    assert len(history) == 3
    assert cascade.summary()["theta"][-1] == history[-1].theta
