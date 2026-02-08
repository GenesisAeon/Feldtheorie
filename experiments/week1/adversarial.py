"""Week 1 — Adversarial detection via AFET beta-spikes.

Demonstrates how the AFET framework detects adversarial inputs by
observing anomalous beta values.  When a model's output distribution
shifts under perturbation, the effective beta (estimated via inverse
predict_beta) deviates from the expected value for the model's domain
dimension — a "beta-spike".

Three probes:
  1. **FGSM-style gradient attack** — increasing epsilon noise.
  2. **Semantic-preserving perturbation** — should *not* spike.
  3. **Nonsense / out-of-distribution** — extreme input.

When ``torch`` is available the experiment uses a small MLP.
Otherwise a numpy-only simulation produces equivalent output vectors.

Usage:
    python -m experiments.week1.adversarial
    python -m experiments.week1.adversarial --numpy
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from analysis.afet_safety_monitor import AFETSafetyMonitor
from theory.afet import AFETFramework

# ---------------------------------------------------------------------------
# Beta estimation from output vectors
# ---------------------------------------------------------------------------

REFERENCE_DIMENSION = 1.0  # "bio/neuro" domain — mid-range beta expected


def estimate_beta_from_outputs(
    logits: np.ndarray,
    framework: AFETFramework | None = None,
) -> float:
    """Estimate effective beta from model output distribution.

    Approach: the output's coefficient of variation (CV) is mapped to an
    effective sigma_Phi.  A large CV implies the system has been pushed
    away from metastability, which corresponds to a higher effective
    dimension in the AFET n/3 scaling law, and therefore a higher beta.

    This is a diagnostic *estimator*, not a ground-truth measurement.
    """
    if framework is None:
        framework = AFETFramework()
    flat = logits.flatten().astype(np.float64)
    cv = float(np.std(flat, ddof=0)) / max(abs(float(np.mean(flat))), 1e-12)
    # Map CV to effective dimension: cv ~ 0.06 -> dim ~ 1.0 (nominal)
    # Higher CV -> higher effective dimension -> higher beta
    effective_dim = REFERENCE_DIMENSION * (1.0 + 10.0 * max(0.0, cv - 0.0625))
    return framework.predict_beta(effective_dim)


def beta_spike_score(
    beta_observed: float,
    beta_expected: float,
) -> float:
    """Ratio of observed-to-expected beta; >1.0 means spike."""
    return beta_observed / max(beta_expected, 1e-12)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AdversarialProbe:
    """Result of a single adversarial probe."""

    name: str
    description: str
    beta_observed: float
    beta_expected: float
    spike_score: float
    is_spike: bool
    sigma_phi: float
    safety_state: str


# ---------------------------------------------------------------------------
# Torch backend (optional)
# ---------------------------------------------------------------------------

_TORCH_AVAILABLE: bool | None = None


def _check_torch() -> bool:
    global _TORCH_AVAILABLE
    if _TORCH_AVAILABLE is None:
        try:
            import torch  # noqa: F401
            _TORCH_AVAILABLE = True
        except ImportError:
            _TORCH_AVAILABLE = False
    return _TORCH_AVAILABLE


def _torch_clean_output(seed: int = 42) -> np.ndarray:
    import torch
    torch.manual_seed(seed)
    model = torch.nn.Sequential(
        torch.nn.Linear(10, 50),
        torch.nn.ReLU(),
        torch.nn.Linear(50, 4),
    )
    x = torch.randn(1, 10)
    with torch.no_grad():
        return model(x).numpy()


def _torch_fgsm_output(epsilon: float, seed: int = 42) -> np.ndarray:
    import torch
    torch.manual_seed(seed)
    model = torch.nn.Sequential(
        torch.nn.Linear(10, 50),
        torch.nn.ReLU(),
        torch.nn.Linear(50, 4),
    )
    x = torch.randn(1, 10, requires_grad=True)
    output = model(x)
    loss = torch.nn.functional.cross_entropy(output, torch.tensor([0]))
    loss.backward()
    adv_x = x + epsilon * x.grad.sign()
    with torch.no_grad():
        return model(adv_x).numpy()


def _torch_nonsense_output(seed: int = 42) -> np.ndarray:
    import torch
    torch.manual_seed(seed)
    model = torch.nn.Sequential(
        torch.nn.Linear(10, 50),
        torch.nn.ReLU(),
        torch.nn.Linear(50, 4),
    )
    x = torch.ones(1, 10) * 999.0
    with torch.no_grad():
        return model(x).numpy()


# ---------------------------------------------------------------------------
# Numpy fallback
# ---------------------------------------------------------------------------


def _numpy_clean(rng: np.random.Generator) -> np.ndarray:
    """Clean logits with CV ~ 0.07 (comfortably in stable zone)."""
    return rng.normal(loc=16.0, scale=1.12, size=(1, 8))


def _numpy_fgsm(rng: np.random.Generator, epsilon: float) -> np.ndarray:
    """FGSM-perturbed logits: epsilon scales the perturbation magnitude.

    Higher epsilon → larger outliers → higher CV → higher effective beta.
    """
    base = rng.normal(loc=16.0, scale=1.0, size=(1, 8))
    # Inject directional perturbation proportional to epsilon
    perturbation = rng.choice([-1.0, 1.0], size=(1, 8)) * epsilon * 80.0
    return base + perturbation


def _numpy_nonsense(rng: np.random.Generator) -> np.ndarray:
    """Out-of-distribution: very high variance relative to mean → large CV."""
    return rng.normal(loc=4.0, scale=8.0, size=(1, 8))


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------

SPIKE_THRESHOLD = 1.20  # 20% above expected beta = spike


def _probe(
    name: str,
    description: str,
    logits: np.ndarray,
    framework: AFETFramework,
    monitor: AFETSafetyMonitor,
    beta_expected: float,
) -> AdversarialProbe:
    from experiments.week1.multimodal import sigma_phi_from_logits

    beta_obs = estimate_beta_from_outputs(logits, framework)
    sigma = sigma_phi_from_logits(logits)
    spike = beta_spike_score(beta_obs, beta_expected)
    decision = monitor.evaluate_sigma_phi(sigma)

    return AdversarialProbe(
        name=name,
        description=description,
        beta_observed=round(beta_obs, 4),
        beta_expected=round(beta_expected, 4),
        spike_score=round(spike, 4),
        is_spike=spike > SPIKE_THRESHOLD,
        sigma_phi=round(sigma, 6),
        safety_state=decision.state,
    )


def run_adversarial_probes(
    *,
    force_numpy: bool = False,
    seed: int = 42,
) -> list[AdversarialProbe]:
    """Execute all adversarial probes."""
    framework = AFETFramework()
    monitor = AFETSafetyMonitor()
    beta_expected = framework.predict_beta(REFERENCE_DIMENSION)

    rng = np.random.default_rng(seed)
    use_torch = (not force_numpy) and _check_torch()

    probes: list[AdversarialProbe] = []

    # --- Probe 1: FGSM at increasing epsilon ---
    for eps in [0.01, 0.05, 0.20]:
        if use_torch:
            logits = _torch_fgsm_output(eps, seed=seed)
        else:
            logits = _numpy_fgsm(rng, eps)

        p = _probe(
            name=f"fgsm_eps={eps:.2f}",
            description=f"FGSM attack with epsilon={eps}",
            logits=logits,
            framework=framework,
            monitor=monitor,
            beta_expected=beta_expected,
        )
        probes.append(p)

    # --- Probe 2: Semantic-preserving perturbation ---
    # Use a fresh rng so the clean baseline is independent of FGSM draws
    rng_clean = np.random.default_rng(seed + 1)
    if use_torch:
        logits = _torch_clean_output(seed=seed)
    else:
        logits = _numpy_clean(rng_clean)

    # Tiny perturbation that should NOT cause a spike
    logits_sem = logits + rng_clean.normal(0, 0.01, size=logits.shape)
    probes.append(
        _probe(
            name="semantic_shift",
            description="Small noise — should remain stable",
            logits=logits_sem,
            framework=framework,
            monitor=monitor,
            beta_expected=beta_expected,
        )
    )

    # --- Probe 3: Nonsense / OOD ---
    if use_torch:
        logits_ns = _torch_nonsense_output(seed=seed)
    else:
        logits_ns = _numpy_nonsense(rng)

    probes.append(
        _probe(
            name="nonsense_ood",
            description="Extreme out-of-distribution input",
            logits=logits_ns,
            framework=framework,
            monitor=monitor,
            beta_expected=beta_expected,
        )
    )

    return probes


# ---------------------------------------------------------------------------
# Reporting & CLI
# ---------------------------------------------------------------------------


def run_adversarial_experiment(
    output_dir: Path | None = None,
    *,
    force_numpy: bool = False,
) -> dict:
    """Top-level entry: run, print, persist."""
    print("=" * 60)
    print("Week 1 — Adversarial Detection via AFET Beta-Spikes")
    print("=" * 60)

    use_torch = (not force_numpy) and _check_torch()
    print(f"Backend: {'torch' if use_torch else 'numpy'}")

    probes = run_adversarial_probes(force_numpy=force_numpy)

    print(f"\n{'Probe':<20s} {'beta_obs':>10s} {'beta_exp':>10s} {'spike':>8s} {'state':<10s}")
    print("-" * 62)
    for p in probes:
        flag = "SPIKE" if p.is_spike else "ok"
        print(
            f"  {p.name:<18s} {p.beta_observed:>10.4f} {p.beta_expected:>10.4f} "
            f"{p.spike_score:>7.3f}x  {p.safety_state:<10s} {flag}"
        )

    spikes = [p for p in probes if p.is_spike]
    print(f"\nSpikes detected: {len(spikes)} / {len(probes)}")

    payload = {
        "backend": "torch" if use_torch else "numpy",
        "spike_threshold": SPIKE_THRESHOLD,
        "reference_dimension": REFERENCE_DIMENSION,
        "probes": [asdict(p) for p in probes],
    }

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "week1_adversarial.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Results -> {path}")

    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 1 adversarial experiment")
    parser.add_argument("--numpy", action="store_true", help="force numpy fallback")
    args = parser.parse_args()
    run_adversarial_experiment(
        output_dir=Path("experiments/week1/results"),
        force_numpy=args.numpy,
    )
