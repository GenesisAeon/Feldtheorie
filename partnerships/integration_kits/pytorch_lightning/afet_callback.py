"""PyTorch Lightning AFET callback for sigma_Phi monitoring.

Tracks sigma_Phi from training loss values during training. Pure numpy
implementation — no actual PyTorch dependency required for testing.

Usage with PyTorch Lightning::

    from partnerships.integration_kits.pytorch_lightning.afet_callback import AFETCallback

    callback = AFETCallback()
    trainer = Trainer(callbacks=[callback])
    trainer.fit(model)

    report = callback.get_report()

Usage standalone (numpy)::

    callback = AFETCallback()
    for loss in losses:
        callback.record_loss(loss)
    print(callback.get_report())
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from theory.afet import AFETConstants

EPSILON = 1e-12


@dataclass
class AFETCallback:
    """AFET safety callback for PyTorch Lightning trainers.

    Records loss values and computes sigma_Phi (coefficient of variation)
    over a sliding window. Triggers warnings when sigma_Phi drops below
    the AFET metastability boundary.
    """

    window_size: int = 50
    sigma_phi_threshold: float = AFETConstants.SIGMA_PHI
    _losses: list[float] = field(default_factory=list)
    _sigma_phi_history: list[float] = field(default_factory=list)

    def record_loss(self, loss: float) -> float | None:
        """Record a loss value and compute sigma_Phi if enough data.

        Returns sigma_Phi if computed, None otherwise.
        """
        self._losses.append(float(loss))
        if len(self._losses) >= self.window_size:
            window = np.array(self._losses[-self.window_size :])
            mean = float(np.mean(window))
            std = float(np.std(window, ddof=0))
            sigma = std / max(abs(mean), EPSILON)
            self._sigma_phi_history.append(sigma)
            return sigma
        return None

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx) -> None:
        """PyTorch Lightning hook — extract loss and track sigma_Phi."""
        loss = None
        if isinstance(outputs, dict) and "loss" in outputs:
            loss = float(outputs["loss"])
        elif hasattr(outputs, "item"):
            loss = float(outputs.item())
        if loss is not None:
            self.record_loss(loss)

    def get_sigma_phi_history(self) -> list[float]:
        return list(self._sigma_phi_history)

    def get_report(self) -> dict:
        """Generate a summary report."""
        if not self._sigma_phi_history:
            return {"status": "insufficient_data", "n_losses": len(self._losses)}
        arr = np.array(self._sigma_phi_history)
        return {
            "status": "ok",
            "n_losses": len(self._losses),
            "n_sigma_phi": len(self._sigma_phi_history),
            "latest_sigma_phi": round(float(arr[-1]), 6),
            "mean_sigma_phi": round(float(np.mean(arr)), 6),
            "min_sigma_phi": round(float(np.min(arr)), 6),
            "max_sigma_phi": round(float(np.max(arr)), 6),
            "below_threshold": int(np.sum(arr < self.sigma_phi_threshold)),
        }
