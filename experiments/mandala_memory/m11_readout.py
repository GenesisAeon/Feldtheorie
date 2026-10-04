"""M11: reading the stored memory better (docs/M11_PLAN_AUSLESE.md, Fassung 2).

The Mandala is unchanged: states z(s, pi) come from the FROZEN M10 functions
(m10_task.network / readout_states, d = 4). This module provides

- exact population balanced accuracy of a fixed linear rule (plan 2.1),
- the population rules of the learning criteria NM(inf), LDA(inf) (plan 2.2),
- the numerical linear reference L_found with the pre-specified optimiser (plan 2.3),
- nested training draws and per-seed test draws (plan 3.1),
- the MLP learning procedure (plan 3.2), numpy only.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np

from experiments.mandala_memory.core import MemoryLabError

_SQRT2 = math.sqrt(2.0)
M11_MODES = {"m11": 11, "m11dev": 12}          # own codes; data.py (frozen M10 code) is not changed


def stream(mode: str, seed: int, *names):
    """Named generator plus its derivation key; same construction as data.stream but
    with M11's own mode codes, so M11 streams can never coincide with earlier ones."""
    import zlib

    if mode not in M11_MODES:
        raise MemoryLabError(f"mode must be one of {tuple(M11_MODES)}")
    key = (int(seed), M11_MODES[mode]) + tuple(zlib.crc32(str(n).encode("utf-8")) for n in names)
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(list(key)))), key


try:                                                  # vectorised Phi; portable fallback without scipy
    from scipy.special import ndtr as _ndtr
except ImportError:                                   # pragma: no cover - exercised in the portable tier
    _ndtr = None


def _phi(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if _ndtr is not None:
        return _ndtr(x)
    return 0.5 * np.array([math.erfc(-v / _SQRT2) for v in x.ravel()]).reshape(x.shape)


# --- plan 2.1 -------------------------------------------------------------------
def exact_accuracy(w: np.ndarray, b: float, z: np.ndarray, probs: np.ndarray, sigma: float) -> float:
    """Population balanced accuracy of 'class B if w.y + b > 0' for y = z(s,pi) + eps,
    eps ~ N(0, sigma^2 I), equal priors; z has shape (2, K, N). w = 0: constant rule, 1/2."""
    w = np.asarray(w, dtype=float)
    nw = float(np.linalg.norm(w))
    if nw == 0.0:
        return 0.5
    s = sigma * nw
    pa = z[0] @ w + b
    pb = z[1] @ w + b
    return float(0.5 * (np.dot(probs, _phi(-pa / s)) + np.dot(probs, _phi(pb / s))))


# --- plan 2.2 -------------------------------------------------------------------
def population_moments(z: np.ndarray, probs: np.ndarray, sigma: float) -> Dict:
    mu = np.array([probs @ z[s] for s in (0, 1)])
    cov = sigma ** 2 * np.eye(z.shape[2])
    for s in (0, 1):
        dz = z[s] - mu[s]
        cov = cov + 0.5 * (dz.T * probs) @ dz
    return {"mu": mu, "pooled_cov": cov}


def population_rules(z: np.ndarray, probs: np.ndarray, sigma: float) -> Dict[str, Tuple[np.ndarray, float]]:
    """Population limits of the learning criteria: NM with the true class means,
    LDA with the true pooled covariance (shrinkage 0); threshold at the midpoint."""
    m = population_moments(z, probs, sigma)
    mu = m["mu"]
    w_nm = mu[1] - mu[0]
    w_lda = np.linalg.solve(m["pooled_cov"], mu[1] - mu[0])
    return {"nm": (w_nm, -0.5 * float(w_nm @ (mu[0] + mu[1]))),
            "lda": (w_lda, -0.5 * float(w_lda @ (mu[0] + mu[1])))}


# --- plan 2.3 -------------------------------------------------------------------
def linear_reference(z: np.ndarray, probs: np.ndarray, sigma: float, rng: np.random.Generator,
                     n_random: int = 20, gtol: float = 1e-10, maxiter: int = 2000) -> Dict:
    """Numerical linear reference L_found (pre-specified optimiser): w = u/||u||, b free,
    L-BFGS-B on -acc with numerical gradient; starts NM(inf), LDA(inf) and n_random random
    directions; NM(inf) and LDA(inf) themselves are non-losable candidates."""
    from scipy.optimize import minimize

    mu = population_moments(z, probs, sigma)["mu"]
    rules = population_rules(z, probs, sigma)

    def obj(theta):
        u, b = theta[:-1], theta[-1]
        nu = np.linalg.norm(u)
        if nu == 0.0:
            return -0.5
        return -exact_accuracy(u / nu, b, z, probs, sigma)

    starts = []
    for name in ("nm", "lda"):
        w, b = rules[name]
        nw = np.linalg.norm(w)
        starts.append((f"{name}_population", np.append(w / nw, b / nw)))
    for k in range(n_random):
        u = rng.normal(size=z.shape[2])
        u /= np.linalg.norm(u)
        starts.append((f"random_{k}", np.append(u, -0.5 * float(u @ (mu[0] + mu[1])))))
    runs = []
    for name, th0 in starts:
        res = minimize(obj, th0, method="L-BFGS-B", options={"gtol": gtol, "maxiter": maxiter})
        runs.append({"start": name, "start_acc": -obj(th0), "end_acc": -float(res.fun), "iterations": int(res.nit),
                     "converged": bool(res.success), "theta": res.x.tolist()})
    candidates = [r["end_acc"] for r in runs] + [exact_accuracy(*rules["nm"], z, probs, sigma),
                                                exact_accuracy(*rules["lda"], z, probs, sigma)]
    best = max(candidates)
    ends = np.array([r["end_acc"] for r in runs])
    return {"L_found": best, "runs": runs, "spread": float(ends.max() - ends.min()),
            "n_within_1e-4_of_best": int(np.sum(ends >= best - 1e-4)),
            "label": "numerical linear reference (best found; lower bound of the linear optimum)"}


# --- plan 3.1 -------------------------------------------------------------------
def draw_pairs(mode: str, seed: int, role: str, n_pairs: int, probs: np.ndarray, N: int, sigma: float) -> Dict:
    """One draw of n_pairs pairs; patterns and noise from SEPARATE streams that do not
    depend on n (prefixes of the maximal draw are the smaller training sets)."""
    rng_p, key_p = stream(mode, seed, "pattern", role)
    rng_e, key_e = stream(mode, seed, "noise", role)
    pi = rng_p.choice(len(probs), size=n_pairs, p=probs / probs.sum())
    eps = rng_e.normal(0.0, sigma, size=(n_pairs, 2, N))
    return {"pattern_index": pi, "noise": eps, "streams": [list(key_p), list(key_e)], "role": role}


def episodes(z: np.ndarray, draw: Dict, n_pairs: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """First n_pairs pairs -> (Y, labels, pair_index); each pair = one A and one B episode."""
    if n_pairs > len(draw["pattern_index"]):
        raise MemoryLabError("prefix longer than the draw")
    pi, eps = draw["pattern_index"][:n_pairs], draw["noise"][:n_pairs]
    Y = np.concatenate([z[0][pi] + eps[:, 0], z[1][pi] + eps[:, 1]])
    labels = np.repeat([0, 1], n_pairs)
    pair = np.concatenate([np.arange(n_pairs), np.arange(n_pairs)])
    return Y, labels, pair


def balanced_accuracy(labels: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([np.mean(pred[labels == c] == c) for c in (0, 1)]))


# --- linear decoders as (w, b) -------------------------------------------------
def nm_rule(Y, labels) -> Tuple[np.ndarray, float]:
    """Nearest-mean without standardisation as a linear rule: class B iff w.y + b > 0
    (identical to d1 < d0; exact ties -> class A as in data.NearestMeanDecoder)."""
    m0, m1 = Y[labels == 0].mean(axis=0), Y[labels == 1].mean(axis=0)
    w = m1 - m0
    return w, -0.5 * float(m1 @ m1 - m0 @ m0)


def lda_rule(Y, labels) -> Tuple[np.ndarray, float]:
    from experiments.mandala_memory.m10_decoders import LedoitWolfLDA

    d = LedoitWolfLDA().fit(Y, labels)
    return d.w, float(d.b)


def predict_linear(w, b, Y) -> np.ndarray:
    return np.where(Y @ w + b > 0, 1, 0)


# --- plan 3.2: MLP learning procedure ------------------------------------------
class MLPDivergence(MemoryLabError):
    """A non-finite value occurred while training the MLP (review M11-R6). Pre-specified
    rule: the whole run fails (no retry, no skipping, no silent fallback)."""


def _check_finite(what: str, *arrays) -> None:
    for a in arrays:
        if not np.all(np.isfinite(a)):
            raise MLPDivergence(f"non-finite {what}")


class MLP:
    """12 -> H tanh -> 1 logistic; BCE + L2 (weights only); Adam, full batch; early
    stopping on validation log-loss (patience, max epochs); standardisation from the
    FIT part only."""

    def __init__(self, hidden: int, lr: float, l2: float, patience: int, max_epochs: int):
        self.H, self.lr, self.l2, self.patience, self.max_epochs = hidden, lr, l2, patience, max_epochs

    def _init(self, rng, d):
        self.p = {"W1": rng.normal(0.0, 1.0 / math.sqrt(d), size=(d, self.H)), "b1": np.zeros(self.H),
                  "w2": rng.normal(0.0, 1.0 / math.sqrt(self.H), size=self.H), "b2": np.zeros(1)}

    def _forward(self, X, p=None):
        p = p or self.p
        h = np.tanh(X @ p["W1"] + p["b1"])
        return h, h @ p["w2"] + p["b2"][0]

    def loss_and_grad(self, X, y, p=None):
        p = p or self.p
        h, logit = self._forward(X, p)
        n = len(y)
        # numerically stable BCE with logits
        loss = float(np.mean(np.maximum(logit, 0) - logit * y + np.log1p(np.exp(-np.abs(logit)))))
        loss += 0.5 * self.l2 * float(np.sum(p["W1"] ** 2) + np.sum(p["w2"] ** 2))
        g = (1.0 / (1.0 + np.exp(-logit)) - y) / n
        grad = {"w2": h.T @ g + self.l2 * p["w2"], "b2": np.array([g.sum()])}
        dh = np.outer(g, p["w2"]) * (1 - h ** 2)
        grad["W1"] = X.T @ dh + self.l2 * p["W1"]
        grad["b1"] = dh.sum(axis=0)
        return loss, grad

    def val_loss(self, X, y, p=None):
        _, logit = self._forward(X, p or self.p)
        return float(np.mean(np.maximum(logit, 0) - logit * y + np.log1p(np.exp(-np.abs(logit)))))

    def fit(self, Xfit, yfit, Xval, yval, rng, deadline=None) -> Dict:
        _check_finite("input", Xfit, yfit, Xval, yval)
        self.mean, self.std = Xfit.mean(axis=0), Xfit.std(axis=0) + 1e-12
        _check_finite("standardisation", self.mean, self.std)
        Xf, Xv = (Xfit - self.mean) / self.std, (Xval - self.mean) / self.std
        self._init(rng, Xf.shape[1])
        m = {k: np.zeros_like(v) for k, v in self.p.items()}
        v2 = {k: np.zeros_like(v) for k, v in self.p.items()}
        best, best_p, since, epoch = math.inf, None, 0, 0
        for epoch in range(1, self.max_epochs + 1):
            if deadline is not None:                          # cooperative time limit, checked every epoch
                deadline()
            loss, grad = self.loss_and_grad(Xf, yfit)
            _check_finite(f"training loss or gradient in epoch {epoch}", np.array([loss]), *grad.values())
            for k in self.p:
                m[k] = 0.9 * m[k] + 0.1 * grad[k]
                v2[k] = 0.999 * v2[k] + 0.001 * grad[k] ** 2
                mh, vh = m[k] / (1 - 0.9 ** epoch), v2[k] / (1 - 0.999 ** epoch)
                self.p[k] = self.p[k] - self.lr * mh / (np.sqrt(vh) + 1e-8)
            _check_finite(f"parameters in epoch {epoch}", *self.p.values())
            vl = self.val_loss(Xv, yval)
            _check_finite(f"validation loss in epoch {epoch}", np.array([vl]))
            if vl < best - 1e-7:
                best, best_p, since = vl, {k: x.copy() for k, x in self.p.items()}, 0
            else:
                since += 1
                if since >= self.patience:
                    break
        self.p = best_p
        return {"best_val_loss": best, "epochs": epoch}

    def predict(self, Y) -> np.ndarray:
        _, logit = self._forward((np.asarray(Y, dtype=float) - self.mean) / self.std)
        return np.where(logit > 0, 1, 0)


def validation_split(n_pairs: int) -> np.ndarray:
    """Fixed rule (no RNG): every 5th PAIR goes to validation -> 20 %, class-stratified,
    the two episodes of a pair always together. Returns a boolean mask over pairs."""
    return (np.arange(n_pairs) % 5) == 4


def fit_mlp(Y, labels, pair, n_pairs, hyper: Dict, mode: str, seed: int, case: str, deadline=None) -> Tuple[MLP, Dict]:
    """All inits are trained; the selected one has the smallest validation log-loss,
    ties -> smallest index (review M11-R7). Full metadata for the gate."""
    val_pairs = validation_split(n_pairs)
    is_val = val_pairs[pair]
    models, infos = [], []
    for k in range(hyper["inits"]):
        rng, key = stream(mode, seed, "mlp-init", case, n_pairs, k)
        model = MLP(hyper["hidden"], hyper["lr"], hyper["l2"], hyper["patience"], hyper["max_epochs"])
        info = model.fit(Y[~is_val], labels[~is_val].astype(float), Y[is_val], labels[is_val].astype(float), rng, deadline)
        models.append(model)
        infos.append({"index": k, "stream": list(key), "best_val_loss": float(info["best_val_loss"]), "epochs": int(info["epochs"])})
    sel = min(range(len(infos)), key=lambda k: (infos[k]["best_val_loss"], k))
    return models[sel], {"hyper": dict(hyper), "inits": infos, "selected": {"init": sel, "best_val_loss": infos[sel]["best_val_loss"],
                                                                           "epochs": infos[sel]["epochs"]},
                         "split_rule": "every 5th pair -> validation", "n_fit_pairs": int((~val_pairs).sum()),
                         "n_val_pairs": int(val_pairs.sum()), "n_fit_episodes": int((~is_val).sum()),
                         "n_val_episodes": int(is_val.sum()), "n_val_class_B": int((is_val & (labels == 1)).sum())}


__all__ = ["exact_accuracy", "population_moments", "population_rules", "linear_reference", "draw_pairs", "episodes",
           "balanced_accuracy", "nm_rule", "lda_rule", "predict_linear", "MLP", "validation_split", "fit_mlp"]
