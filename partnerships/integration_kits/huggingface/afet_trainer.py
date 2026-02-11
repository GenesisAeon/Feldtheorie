"""HuggingFace Transformers AFET trainer mixin.

Provides sigma_Phi monitoring for HuggingFace Trainer subclasses. Pure
numpy implementation — no actual transformers dependency required.

Usage::

    from partnerships.integration_kits.huggingface.afet_trainer import AFETTrainerMixin

    class MyTrainer(AFETTrainerMixin):
        pass

    trainer = MyTrainer()
    trainer.record_loss(0.5)
    report = trainer.get_afet_report()
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from theory.afet import AFETConstants

EPSILON = 1e-12


@dataclass
class AFETTrainerMixin:
    """Mixin that adds AFET sigma_Phi monitoring to a trainer.

    Tracks loss values and computes sigma_Phi over a sliding window.
    """

    afet_window: int = 50
    afet_threshold: float = AFETConstants.SIGMA_PHI
    _afet_losses: list[float] = field(default_factory=list)
    _afet_sigmas: list[float] = field(default_factory=list)

    def record_loss(self, loss: float) -> None:
        """Record a training loss value."""
        self._afet_losses.append(float(loss))
        if len(self._afet_losses) >= self.afet_window:
            window = np.array(self._afet_losses[-self.afet_window :])
            mean = float(np.mean(window))
            std = float(np.std(window, ddof=0))
            sigma = std / max(abs(mean), EPSILON)
            self._afet_sigmas.append(sigma)

    def compute_afet_metrics(self, loss_values: list[float]) -> dict:
        """Compute AFET metrics from a batch of loss values."""
        arr = np.array(loss_values, dtype=np.float64)
        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=0))
        sigma = std / max(abs(mean), EPSILON)
        return {
            "sigma_phi": round(sigma, 6),
            "mean_loss": round(mean, 6),
            "std_loss": round(std, 6),
            "is_stable": sigma >= self.afet_threshold,
        }

    def check_safety(self, sigma_phi: float) -> dict:
        """Check a sigma_Phi value against AFET thresholds."""
        if sigma_phi < 0.055:
            return {"state": "critical", "should_stop": True}
        if sigma_phi < self.afet_threshold:
            return {"state": "warning", "should_stop": False}
        return {"state": "stable", "should_stop": False}

    def get_afet_report(self) -> dict:
        """Generate AFET monitoring report."""
        if not self._afet_sigmas:
            return {"status": "insufficient_data", "n_losses": len(self._afet_losses)}
        arr = np.array(self._afet_sigmas)
        return {
            "status": "ok",
            "n_losses": len(self._afet_losses),
            "n_sigma_phi": len(self._afet_sigmas),
            "latest_sigma_phi": round(float(arr[-1]), 6),
            "mean_sigma_phi": round(float(np.mean(arr)), 6),
            "below_threshold": int(np.sum(arr < self.afet_threshold)),
        }
