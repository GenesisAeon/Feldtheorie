"""M2 prototype: Genesis Orchestrator for multi-agent delegation and telemetry."""

from __future__ import annotations

import time
from typing import Any

from aeon.modules.knowledge_system import KnowledgeSystem
from aeon.nullkern.zero_point_kernel import Nullkern


class GenesisOrchestrator:
    def __init__(self, kernel: Nullkern, knowledge_system: KnowledgeSystem | None = None) -> None:
        self.kernel = kernel
        self.knowledge_system = knowledge_system or KnowledgeSystem()
        self.delegation_log: list[dict[str, Any]] = []

    def delegate(self, agent: str, intent: str, payload: dict[str, Any]) -> dict[str, Any]:
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
        else:
            result["status"] = "ignored"
            result["reason"] = f"unknown intent: {intent}"

        result["duration_ms"] = (time.time() - started) * 1000.0
        self.delegation_log.append(result)
        return result

    def get_aletheia_telemetry(self, resource: float = 0.5, threshold: float = 0.5) -> dict[str, float]:
        return {
            "kappa_metric": float(self.kernel.kappa),
            "sigma_metric": float(self.kernel.activate(resource=resource, threshold=threshold)),
            "aleph_metric": float(self.kernel.get_information_density()),
            "delegation_count": float(len(self.delegation_log)),
        }
