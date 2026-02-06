"""
Ethics Guard
============

Part of the GenesisAeon Feldtheorie project.
License: LGPL-3.0-or-later

Stellt Consent & Audit-Trail sicher. Die Guard hält ζ(R) gedämpft,
indem sie Warnungen protokolliert und σ(β(R-Θ)) nur bei gültigem
Consent öffnet.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re


class EthicsViolation(RuntimeError):
    pass


@dataclass
class EthicsWarning:
    code: str
    message: str


@dataclass
class EthicsReport:
    action: str
    warnings: list[EthicsWarning]


class EthicsGuard:
    _HASH_SALT = "ethics-guard"

    def __init__(self, audit_log_path: str | Path) -> None:
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def check_before_analysis(
        self,
        *,
        location: str,
        crep: float,
        consent_granted: bool,
        subject_hash: str,
        crep_warning_threshold: float = 0.70,
        tag: str = "v12",
    ) -> EthicsReport:
        if not consent_granted:
            raise EthicsViolation("CONSENT_REQUIRED")

        anonymized_subject = self._normalize_subject_hash(subject_hash)

        warnings: list[EthicsWarning] = []
        if location == "public":
            warnings.append(
                EthicsWarning(
                    code="PUBLIC_MODE_RISK",
                    message="Reduced granularity recommended for public contexts.",
                )
            )
        if crep < crep_warning_threshold:
            warnings.append(
                EthicsWarning(
                    code="FRAME_DRIFT",
                    message="Recalibration advised (CREP below threshold).",
                )
            )

        if warnings:
            self._log_warnings(anonymized_subject, warnings, tag=tag)

        return EthicsReport(action="proceed", warnings=warnings)

    def _normalize_subject_hash(self, subject_hash: str) -> str:
        if re.fullmatch(r"[a-f0-9]{64}", subject_hash):
            return subject_hash
        return self._hash_value(subject_hash)

    def _hash_value(self, value: str) -> str:
        payload = f"{self._HASH_SALT}:{value}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _log_warnings(self, subject_hash: str, warnings: list[EthicsWarning], *, tag: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self.audit_log_path.open("a", encoding="utf-8") as handle:
            for warning in warnings:
                handle.write(
                    f"[{timestamp}] [{tag}] [{subject_hash}] [{warning.code}] {warning.message}\n"
                )
