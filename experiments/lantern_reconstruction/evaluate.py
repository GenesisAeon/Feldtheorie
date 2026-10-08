"""LR4 evaluation of a frozen decoder on test features (plan sections 9, 11).

Imports prediction and metrics only -- never a fit function (plan 11; checked by a test). The decoder
reaches this module finished; test targets enter only here, after the fit."""
from __future__ import annotations

from typing import Dict

import numpy as np

from experiments.lantern_reconstruction.decoders import RidgeDecoder, predict
from experiments.lantern_reconstruction.metrics import episode_losses, project, scores


def score_cell(model: RidgeDecoder, X_test, U_test) -> Dict:
    """Raw and projected predictions, per-episode losses, S and G of one (context, condition, task, time) cell."""
    raw = predict(model, X_test)
    proj = project(raw)
    loss, loss_zero = episode_losses(proj, U_test)
    return {**scores(loss, loss_zero), "raw": raw, "projected": proj, "loss": loss, "loss_zero": loss_zero,
            "n_raw_outside_unit_box": int(np.sum(np.abs(raw) > 1.0))}
