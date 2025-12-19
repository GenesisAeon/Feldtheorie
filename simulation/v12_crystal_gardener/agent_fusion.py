"""Crystal Gardener (V12): Fusion of σ_Φ cultivation with crystal oracle vetoes."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import Dict, List, Tuple

import numpy as np

from simulation.v10_oracle import CrystalOracle
from v10_oracle.models.semantic_bridge import ResonanceTranslator
from v11_gardener.agents.sigma_phi_gardener import (
    AgentHealth,
    CultivationAction,
    SigmaPhiGardener,
)


class CrystalGardener(SigmaPhiGardener):
    """Fuse the σ_Φ gardener with a CrystalOracle "inner ear".

    The inner oracle evaluates planned cultivation moves against a stabilized
    seed (random_state=2048). Actions that push the oracle outside the
    resonance band (σ_ϕ ∉ [0.06, 0.07]) are vetoed. Actions that land in the
    lucid band (LUCID_RESONANCE ≈ [0.060, 0.065]) are amplified to prevent
    pressure-induced paralysis.
    """

    def __init__(
        self,
        *,
        oracle_seed: int = 2048,
        resonance_band: Tuple[float, float] = (0.06, 0.07),
        lucid_band: Tuple[float, float] = (0.060, 0.065),
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.oracle_seed = oracle_seed
        self.resonance_band = resonance_band
        self.lucid_band = lucid_band

        self.inner_oracle = CrystalOracle(random_state=oracle_seed)
        self.translator = ResonanceTranslator(
            base_frequency=1.0, golden_band=lucid_band, slowing_threshold=0.025
        )

        self.oracle_vetoes = 0
        self.resonance_assists = 0
        self.oracle_journal: List[Dict[str, object]] = []

    def cultivate_ecosystem(
        self,
        agent_states: Dict[str, Dict[str, float]],
        coupling_matrix: np.ndarray,
        agent_ids: List[str],
        timestep: int = 0,
    ) -> Tuple[np.ndarray, Dict[str, float], List[AgentHealth]]:
        """Cultivate with oracle-gated actions."""

        assessments: List[AgentHealth] = []
        adjusted_matrix = coupling_matrix.copy()
        adjusted_temps: Dict[str, float] = {}

        for i, agent_id in enumerate(agent_ids):
            if agent_id not in agent_states:
                continue

            state = agent_states[agent_id]
            assessment = self.assess_agent(
                agent_id=agent_id,
                sigma_phi=state.get("sigma_phi", 0.0),
                entropy=state.get("entropy", 0.0),
                temperature=state.get("temperature", 1.0),
                kappa_total=state.get("kappa_total", 0.0),
                resonance_quality=state.get("resonance_quality", 0.5),
            )

            guided_assessment = self.decide_action(assessment)
            assessments.append(guided_assessment)

            temp_adjustment = self._apply_action(
                assessment=guided_assessment,
                agent_idx=i,
                coupling_matrix=adjusted_matrix,
            )

            adjusted_temps[agent_id] = temp_adjustment

        adjusted_matrix = (adjusted_matrix + adjusted_matrix.T) / 2
        self._record_cycle(timestep, assessments)
        self._detect_emergence(assessments, timestep)

        return adjusted_matrix, adjusted_temps, assessments

    def decide_action(self, assessment: AgentHealth) -> AgentHealth:
        """Run the planned action through the oracle before execution."""

        encoded = self._encode_action_vector(assessment)
        dream = self.inner_oracle.dream(encoded)
        resonance_state = dream.final_state
        sigma_phi_est = self._estimate_sigma_phi(resonance_state)
        global_coherence = float(np.mean(np.abs(resonance_state)))
        translation = self.translator.translate(
            sigma_phi=sigma_phi_est, global_coherence=global_coherence, frequency=1.0
        )

        veto = sigma_phi_est < self.resonance_band[0] or sigma_phi_est > self.resonance_band[1]

        decision = "pass"
        new_action = assessment.recommended_action
        new_strength = assessment.action_strength

        if veto:
            decision = "veto"
            new_action = CultivationAction.OBSERVE
            new_strength = 0.0
            self.oracle_vetoes += 1
        elif translation.state == "LUCID_RESONANCE":
            decision = "resonance_boost"
            new_strength = min(1.0, assessment.action_strength * 1.2)
            self.resonance_assists += 1

        self.oracle_journal.append(
            {
                "agent_id": assessment.agent_id,
                "proposed_action": assessment.recommended_action.value,
                "final_action": new_action.value,
                "sigma_phi_est": sigma_phi_est,
                "coherence": global_coherence,
                "translation": translation.state,
                "decision": decision,
            }
        )

        if new_action != assessment.recommended_action or not np.isclose(
            new_strength, assessment.action_strength
        ):
            return replace(assessment, recommended_action=new_action, action_strength=new_strength)

        return assessment

    def _encode_action_vector(self, assessment: AgentHealth) -> np.ndarray:
        """Encode an action and health snapshot into a 16D seed."""

        payload = (
            f"{assessment.agent_id}|{assessment.recommended_action.value}|"
            f"{assessment.sigma_phi:.5f}|{assessment.temperature:.3f}|"
            f"{assessment.resonance_quality:.3f}|{self.oracle_seed}"
        )
        digest = hashlib.sha256(payload.encode("utf-8")).digest()
        base = (np.frombuffer(digest[:16], dtype=np.uint8).astype(float) - 127.5) / 127.5

        modulation_rng = np.random.default_rng(self.oracle_seed)
        modulation = modulation_rng.normal(loc=0.0, scale=0.03, size=16)
        return base + modulation

    def _estimate_sigma_phi(self, resonance_state: np.ndarray) -> float:
        """Project oracle resonance into a σ_ϕ estimate near the golden band."""

        dispersion = float(np.std(resonance_state))
        coherence = float(np.mean(np.abs(resonance_state)))
        sigma_phi_est = 0.0625 + 0.02 * np.tanh(dispersion + (1.0 - coherence))
        return float(np.clip(sigma_phi_est, 0.0, 0.2))

    def oracle_summary(self) -> Dict[str, object]:
        """Return metrics on oracle interventions."""

        return {
            "oracle_seed": self.oracle_seed,
            "resonance_band": self.resonance_band,
            "lucid_band": self.lucid_band,
            "vetoes": self.oracle_vetoes,
            "resonance_assists": self.resonance_assists,
            "recent_decisions": self.oracle_journal[-10:],
        }


__all__ = ["CrystalGardener"]
