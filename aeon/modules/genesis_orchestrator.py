"""M2 prototype: Genesis Orchestrator for multi-agent delegation, CREP, and telemetry."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from aeon.modules.architecture_spec import get_core_module_contracts
from aeon.modules.knowledge_system import KnowledgeSystem
from aeon.nullkern.zero_point_kernel import Nullkern


@dataclass
class AgentRecord:
    """Registered agent with its capabilities."""

    name: str
    capabilities: list[str] = field(default_factory=list)
    delegation_count: int = 0


class GenesisOrchestrator:
    """Multi-agent coordination, CREP quality control, and Nullkern interface.

    Responsibilities:
    - Register agents with declared capabilities
    - Route delegations to agents
    - Validate delegation results via CREP quality checks
    - Expose Nullkern lifecycle snapshots
    - Broadcast messages to all registered agents
    - Produce Aletheia-compatible telemetry
    """

    def __init__(
        self,
        kernel: Nullkern,
        knowledge_system: KnowledgeSystem | None = None,
    ) -> None:
        self.kernel = kernel
        self.knowledge_system = knowledge_system or KnowledgeSystem()
        self.delegation_log: list[dict[str, Any]] = []
        self.agents: dict[str, AgentRecord] = {}
        self._crep_scores: list[float] = []

    # ------------------------------------------------------------------
    # Agent registration
    # ------------------------------------------------------------------

    def register_agent(
        self,
        name: str,
        capabilities: list[str] | None = None,
    ) -> None:
        if name in self.agents:
            raise ValueError(f"Agent '{name}' is already registered")
        self.agents[name] = AgentRecord(
            name=name,
            capabilities=capabilities or [],
        )

    # ------------------------------------------------------------------
    # Delegation
    # ------------------------------------------------------------------

    def delegate(
        self,
        agent: str,
        intent: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        started = time.time()
        result: dict[str, Any] = {
            "agent": agent,
            "intent": intent,
            "status": "completed",
            "duration_ms": 0.0,
        }

        if intent == "summarize":
            topic = str(payload.get("topic", "general"))
            content = str(payload.get("content", ""))
            entry_id = f"{agent.lower()}.{topic.lower()}"
            self.knowledge_system.upsert(entry_id, content)
            result["knowledge_entry"] = entry_id
            result["summary"] = content[:160]
        elif intent == "query_knowledge":
            query = str(payload.get("query", ""))
            result["hits"] = self.knowledge_system.query(query)
        elif intent == "nullkern_validation":
            result["validation"] = self.kernel.self_referential_validate(recursion_depth=8)
        elif intent == "status_check":
            result["snapshot"] = self.get_nullkern_snapshot()
        else:
            result["status"] = "ignored"
            result["reason"] = f"unknown intent: {intent}"

        result["duration_ms"] = (time.time() - started) * 1000.0
        self.delegation_log.append(result)

        # Track per-agent delegation count
        if agent in self.agents:
            self.agents[agent].delegation_count += 1

        return result

    # ------------------------------------------------------------------
    # Multi-agent broadcast
    # ------------------------------------------------------------------

    def broadcast(
        self,
        intent: str,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Send a delegation to every registered agent."""
        return [
            self.delegate(name, intent, payload)
            for name in self.agents
        ]

    # ------------------------------------------------------------------
    # CREP quality control
    # ------------------------------------------------------------------

    def crep_validate(self, delegation_result: dict[str, Any]) -> dict[str, Any]:
        """Validate a delegation result using CREP (Coherence-Resonance-Ethics-Precision).

        Scoring:
        - Coherence:  status == 'completed' → 1.0
        - Resonance:  summary or hits present → 1.0
        - Ethics:     no sensitive data leak → 1.0 (always passes here)
        - Precision:  duration < 1000ms → 1.0, else scaled
        """
        coherence = 1.0 if delegation_result.get("status") == "completed" else 0.0

        has_content = bool(
            delegation_result.get("summary")
            or delegation_result.get("hits")
            or delegation_result.get("validation")
            or delegation_result.get("snapshot")
        )
        resonance = 1.0 if has_content else 0.0

        ethics = 1.0  # Structural — no PII or secret leak in this layer

        duration = delegation_result.get("duration_ms", 0.0)
        precision = min(1.0, 1000.0 / (duration + 1.0))

        quality_score = (coherence + resonance + ethics + precision) / 4.0
        passed = quality_score >= 0.5

        self._crep_scores.append(quality_score)

        return {
            "coherence": coherence,
            "resonance": resonance,
            "ethics": ethics,
            "precision": precision,
            "quality_score": quality_score,
            "passed": passed,
        }

    # ------------------------------------------------------------------
    # Nullkern interface
    # ------------------------------------------------------------------

    def get_nullkern_snapshot(self) -> dict[str, Any]:
        """Return a lifecycle snapshot of the Nullkern."""
        return self.kernel.get_state_summary()

    def get_core_module_contracts(self) -> dict[str, dict[str, object]]:
        """Expose formalized contracts for MasterGPT/TutorGPT/etc. coordination."""
        return get_core_module_contracts()

    # ------------------------------------------------------------------
    # Telemetry
    # ------------------------------------------------------------------

    def get_aletheia_telemetry(
        self,
        resource: float = 0.5,
        threshold: float = 0.5,
    ) -> dict[str, float]:
        mean_crep = (
            sum(self._crep_scores) / len(self._crep_scores)
            if self._crep_scores
            else 0.0
        )
        return {
            "kappa_metric": float(self.kernel.kappa),
            "sigma_metric": float(
                self.kernel.activate(resource=resource, threshold=threshold)
            ),
            "aleph_metric": float(self.kernel.get_information_density()),
            "delegation_count": float(len(self.delegation_log)),
            "crep_mean_score": float(mean_crep),
        }
