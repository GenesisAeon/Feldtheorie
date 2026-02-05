"""
NeuroProfile Model
=================

Verknüpft β-Schätzung, σΦ-Proxy und Resonanzvergleich.
R, Θ, β und ζ(R) werden im Modellkontext explizit benannt,
σ(β(R-Θ)) bleibt als Kontrollfunktion präsent.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Callable, Sequence

import numpy as np

from .beta_extractor_neuro import BetaEstimate, estimate_beta_from_series
from .crep_calculator import CrepResult, compute_crep
from .ethics_guard import EthicsGuard, EthicsReport
from .microtubule_resonance import ResonanceProxyResult, estimate_resonance_proxy
from .resonant_return import ResonantReturnConfig, ResonantReturnResult, analyze_resonant_return
from .lanternnet_ledgers import log_lanternnet_ledgers

CONSENT_MESSAGE = (
    "Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration."
)


@dataclass
class NeuroProfileConfig:
    sampling_rate: float = 256.0
    sigma_phi_target: float = 0.0625
    logistic_R: float = 0.46
    logistic_Theta: float = 0.72
    logistic_beta: float = 4.8
    zeta_R: float = 0.19
    v_rig_target_kms: float = 1.352
    bootstrap_samples: int = 200
    bootstrap_seed: int = 23
    anonymization_salt: str = "neuroprofile"
    crep_beta_baseline: float = 7.4
    crep_warning_threshold: float = 0.70
    neuroprofile_version: str = "v13.0.0"
    enable_lanternnet_logging: bool = False
    lanternnet_bootstrap_ledger_path: Path = Path("data/bootstrap_ledger.json")
    lanternnet_crep_ledger_path: Path = Path("data/crep_null_model_ledger.json")
    lanternnet_module_id: str = "exp-neuroprofile-001"
    lanternnet_module_name: str = "NeuroProfile Resonance Bridge"


@dataclass
class ConsentRecord:
    message: str
    granted: bool
    anonymized_subject: str | None
    consent_token_hash: str | None
    timestamp: str


@dataclass
class NullModelSummary:
    best_model: str
    aic: dict[str, float]
    delta_aic: dict[str, float]
    parameters: dict[str, dict[str, float]]


@dataclass
class NullModelBootstrapEntry:
    iteration: int
    best_model: str
    delta_aic: dict[str, float]


@dataclass
class NeuroProfileResult:
    beta_estimate: BetaEstimate
    beta_ci: tuple[float, float]
    sigma_phi_proxy: float
    sigma_phi_ci: tuple[float, float]
    resonance_proxy: ResonanceProxyResult
    gamma_beta_ci: tuple[float, float]
    resonance_alignment_ci: tuple[float, float]
    resonant_return: ResonantReturnResult
    crep: CrepResult
    ethics_report: EthicsReport
    null_models: NullModelSummary
    null_model_bootstrap: list[NullModelBootstrapEntry]
    consent: ConsentRecord


class NeuroProfileModel:
    def __init__(self, config: NeuroProfileConfig | None = None) -> None:
        self.config = config or NeuroProfileConfig()
        audit_path = Path(__file__).resolve().parents[1] / "data" / "ethics_audit.log"
        self.ethics_guard = EthicsGuard(audit_path)

    def preprocess(self, series: Sequence[float]) -> np.ndarray:
        data = np.asarray(series, dtype=float)
        if data.size == 0:
            return data
        return (data - np.mean(data)) / (np.std(data) + 1e-9)

    def estimate_sigma_phi_proxy(self, series: np.ndarray) -> float:
        """Estimate σΦ (spectral entropy) proxy from time series."""
        # Handle empty or very short series
        if series.size < 2:
            return 0.0
        # Proxy: normalized spectral entropy
        spectrum = np.abs(np.fft.rfft(series)) ** 2
        if spectrum.size == 0:
            return 0.0
        spectrum = spectrum / (np.sum(spectrum) + 1e-9)
        entropy = -np.sum(spectrum * np.log(spectrum + 1e-9))
        entropy_norm = entropy / np.log(spectrum.size + 1e-9)
        return float(entropy_norm)

    def _aic(self, rss: float, n: int, k: int) -> float:
        return float(n * np.log(rss / n + 1e-12) + 2 * k)

    def _fit_null_models(self, series: np.ndarray) -> NullModelSummary:
        if series.size == 0:
            return NullModelSummary(
                best_model="constant",
                aic={"constant": 0.0, "linear": 0.0, "power_law": 0.0},
                delta_aic={"constant": 0.0, "linear": 0.0, "power_law": 0.0},
                parameters={"constant": {"mean": 0.0}, "linear": {"slope": 0.0, "intercept": 0.0}, "power_law": {"a": 0.0, "b": 0.0}},
            )

        y = np.abs(series)
        x = np.arange(1, y.size + 1, dtype=float)

        y_mean = float(np.mean(y))
        rss_const = float(np.sum((y - y_mean) ** 2))
        aic_const = self._aic(rss_const, y.size, 1)

        x_mat = np.column_stack((np.ones_like(x), x))
        coef, *_ = np.linalg.lstsq(x_mat, y, rcond=None)
        intercept, slope = coef
        y_pred_lin = intercept + slope * x
        rss_lin = float(np.sum((y - y_pred_lin) ** 2))
        aic_lin = self._aic(rss_lin, y.size, 2)

        log_x = np.log(x)
        log_y = np.log(y + 1e-12)
        pl_coef, *_ = np.linalg.lstsq(np.column_stack((np.ones_like(log_x), log_x)), log_y, rcond=None)
        log_a, b = pl_coef
        a = float(np.exp(log_a))
        y_pred_pl = a * (x**b)
        rss_pl = float(np.sum((y - y_pred_pl) ** 2))
        aic_pl = self._aic(rss_pl, y.size, 2)

        aic = {"constant": aic_const, "linear": aic_lin, "power_law": aic_pl}
        min_aic = min(aic.values())
        delta_aic = {name: float(value - min_aic) for name, value in aic.items()}
        best_model = min(aic, key=aic.get)

        return NullModelSummary(
            best_model=best_model,
            aic=aic,
            delta_aic=delta_aic,
            parameters={
                "constant": {"mean": y_mean},
                "linear": {"intercept": float(intercept), "slope": float(slope)},
                "power_law": {"a": float(a), "b": float(b)},
            },
        )

    def _bootstrap_ci(self, series: np.ndarray, metric_fn: Callable[[np.ndarray], float]) -> tuple[float, float]:
        if series.size == 0:
            return (0.0, 0.0)
        rng = np.random.default_rng(self.config.bootstrap_seed)
        indices = np.arange(series.size)
        samples = []
        for _ in range(self.config.bootstrap_samples):
            draw = rng.choice(indices, size=indices.size, replace=True)
            samples.append(metric_fn(series[draw]))
        low, high = np.percentile(samples, [2.5, 97.5])
        return (float(low), float(high))

    def _bootstrap_null_models(self, series: np.ndarray) -> list[NullModelBootstrapEntry]:
        if series.size == 0:
            return []
        rng = np.random.default_rng(self.config.bootstrap_seed)
        indices = np.arange(series.size)
        ledger: list[NullModelBootstrapEntry] = []
        for iteration in range(1, self.config.bootstrap_samples + 1):
            draw = rng.choice(indices, size=indices.size, replace=True)
            summary = self._fit_null_models(series[draw])
            ledger.append(
                NullModelBootstrapEntry(
                    iteration=iteration,
                    best_model=summary.best_model,
                    delta_aic=summary.delta_aic,
                )
            )
        return ledger

    def _require_consent(self, granted: bool, consent_token: str | None) -> str:
        if not granted:
            raise PermissionError(f"{CONSENT_MESSAGE} Consent not granted.")
        if not consent_token:
            raise PermissionError(f"{CONSENT_MESSAGE} Consent token required.")
        return self._hash_value("consent-token", consent_token)

    def _hash_value(self, namespace: str, value: str) -> str:
        payload = f"{self.config.anonymization_salt}:{namespace}:{value}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _anonymize_subject(self, subject_id: str) -> str:
        return self._hash_value("subject", subject_id)

    def analyze(
        self,
        series: Sequence[float],
        *,
        consent_granted: bool = False,
        consent_token: str | None = None,
        subject_id: str | None = None,
        context_location: str = "lab",
        source_id: str = "analysis-run",
        log_to_lanternnet: bool | None = None,
    ) -> NeuroProfileResult:
        consent_token_hash = self._require_consent(consent_granted, consent_token)
        prepared = self.preprocess(series)
        beta_estimate = estimate_beta_from_series(prepared)
        sigma_phi_proxy = self.estimate_sigma_phi_proxy(prepared)
        resonance_proxy = estimate_resonance_proxy(prepared, self.config.sampling_rate)
        resonant_return = analyze_resonant_return(
            prepared,
            config=ResonantReturnConfig(
                sigma_phi_target=self.config.sigma_phi_target,
                v_rig_target_kms=self.config.v_rig_target_kms,
            ),
        )
        crep = compute_crep(
            beta_estimate.beta,
            sigma_phi_proxy,
            prepared,
            self.config.sampling_rate,
            sigma_phi_target=self.config.sigma_phi_target,
            beta_baseline=self.config.crep_beta_baseline,
        )
        null_models = self._fit_null_models(prepared)
        null_model_bootstrap = self._bootstrap_null_models(prepared)
        beta_ci = self._bootstrap_ci(prepared, lambda sample: estimate_beta_from_series(sample).beta)
        sigma_phi_ci = self._bootstrap_ci(prepared, self.estimate_sigma_phi_proxy)
        gamma_beta_ci = self._bootstrap_ci(
            prepared,
            lambda sample: estimate_resonance_proxy(sample, self.config.sampling_rate).gamma_beta_coupling,
        )
        resonance_alignment_ci = self._bootstrap_ci(
            prepared,
            lambda sample: estimate_resonance_proxy(sample, self.config.sampling_rate).proxy_alignment,
        )
        anonymized = self._anonymize_subject(subject_id) if subject_id else None
        ethics_report = self.ethics_guard.check_before_analysis(
            location=context_location,
            crep=crep.aggregate,
            consent_granted=consent_granted,
            subject_hash=anonymized or "anonymous",
            crep_warning_threshold=self.config.crep_warning_threshold,
            tag=self.config.neuroprofile_version,
        )
        result = NeuroProfileResult(
            beta_estimate=beta_estimate,
            beta_ci=beta_ci,
            sigma_phi_proxy=sigma_phi_proxy,
            sigma_phi_ci=sigma_phi_ci,
            resonance_proxy=resonance_proxy,
            gamma_beta_ci=gamma_beta_ci,
            resonance_alignment_ci=resonance_alignment_ci,
            resonant_return=resonant_return,
            crep=crep,
            ethics_report=ethics_report,
            null_models=null_models,
            null_model_bootstrap=null_model_bootstrap,
            consent=ConsentRecord(
                message=CONSENT_MESSAGE,
                granted=consent_granted,
                anonymized_subject=anonymized,
                consent_token_hash=consent_token_hash,
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
        )
        should_log = self.config.enable_lanternnet_logging if log_to_lanternnet is None else log_to_lanternnet
        if should_log:
            log_lanternnet_ledgers(
                result=result,
                config=self.config,
                module_id=self.config.lanternnet_module_id,
                module_name=self.config.lanternnet_module_name,
                source_id=source_id,
                seed=self.config.bootstrap_seed,
                bootstrap_ledger_path=self.config.lanternnet_bootstrap_ledger_path,
                crep_ledger_path=self.config.lanternnet_crep_ledger_path,
            )
        return result


class NeuroProfile:
    def __init__(self, subject_id: str | None = None, config: NeuroProfileConfig | None = None) -> None:
        self.subject_id = subject_id
        self.model = NeuroProfileModel(config=config)
        self.series: np.ndarray | None = None
        self.result: NeuroProfileResult | None = None

    def load_synthetic_data(self, *, size: int = 2048, seed: int = 42) -> np.ndarray:
        rng = np.random.default_rng(seed)
        self.series = rng.normal(0.0, 1.0, size)
        return self.series

    def analyze(
        self,
        *,
        consent_granted: bool = True,
        consent_token: str | None = None,
        context_location: str = "lab",
        source_id: str = "analysis-run",
        log_to_lanternnet: bool | None = None,
    ) -> NeuroProfileResult:
        if self.series is None:
            raise ValueError("No data loaded. Call load_synthetic_data or provide series first.")
        self.result = self.model.analyze(
            self.series,
            consent_granted=consent_granted,
            consent_token=consent_token,
            subject_id=self.subject_id,
            context_location=context_location,
            source_id=source_id,
            log_to_lanternnet=log_to_lanternnet,
        )
        return self.result


def run_demo() -> NeuroProfileResult:
    rng = np.random.default_rng(42)
    synthetic = rng.normal(0.0, 1.0, 2048)
    model = NeuroProfileModel()
    return model.analyze(
        synthetic,
        consent_granted=True,
        consent_token="demo-consent-token",
        subject_id="demo-subject",
        source_id="synthetic-demo",
        log_to_lanternnet=True,
    )


if __name__ == "__main__":
    result = run_demo()
    print(result)
