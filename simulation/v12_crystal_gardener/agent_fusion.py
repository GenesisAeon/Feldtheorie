"""Crystal Gardener (V12): Fusion of σ_Φ cultivation with crystal oracle vetoes."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import Dict, List, Tuple

import numpy as np

from simulation.v10_oracle import CrystalOracle
from v10_oracle.models.semantic_bridge import ResonanceTranslator
from v11_gardener.core.constants import is_alive
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
        self.lazarus_mode_active = False
        self.network_pressure_trace: List[float] = []
        self.network_engagement_trace: List[bool] = []

    def form_mycelial_network(
        self, ecosystem: Dict[str, object], current_pressure: float
    ) -> Dict[str, float]:
        """Form a virtual mycelial network to distribute pressure.

        When the environment pressure rises above 2 atm, agents connect and
        share load. The effective pressure is damped by the network size,
        mirroring how crystalline lattices distribute stress.
        """

        agent_states = ecosystem.get("agent_states", {})
        agent_ids = ecosystem.get("agent_ids", list(agent_states.keys()))

        connected_agents = [agent_id for agent_id in agent_ids if agent_id in agent_states]
        connected_agents_count = max(1, len(connected_agents))

        effective_pressure = current_pressure
        network_engaged = False
        if current_pressure > 2.0:
            effective_pressure = current_pressure / float(
                np.sqrt(connected_agents_count)
            )
            network_engaged = True

        mean_sigma_phi = float(
            np.mean([agent_states[a]["sigma_phi"] for a in connected_agents])
        ) if connected_agents else 0.0
        mean_resonance_quality = float(
            np.mean(
                [agent_states[a].get("resonance_quality", 0.0) for a in connected_agents]
            )
        ) if connected_agents else 0.0

        self.network_pressure_trace.append(effective_pressure)
        self.network_engagement_trace.append(network_engaged)

        if network_engaged:
            print(f"Effective Network Pressure: {effective_pressure:.2f} atm")

        return {
            "network_engaged": network_engaged,
            "effective_pressure": effective_pressure,
            "connected_agents": connected_agents_count,
            "mean_sigma_phi": mean_sigma_phi,
            "mean_resonance_quality": mean_resonance_quality,
        }

    def cultivate_ecosystem(
        self,
        agent_states: Dict[str, Dict[str, float]],
        coupling_matrix: np.ndarray,
        agent_ids: List[str],
        timestep: int = 0,
        current_pressure: float = 1.0,
    ) -> Tuple[np.ndarray, Dict[str, float], List[AgentHealth]]:
        """Cultivate with oracle-gated actions."""

        assessments: List[AgentHealth] = []
        adjusted_matrix = coupling_matrix.copy()
        adjusted_temps: Dict[str, float] = {}

        total_agents = len([agent_id for agent_id in agent_ids if agent_id in agent_states])
        alive_agents = sum(
            1
            for agent_id in agent_ids
            if agent_id in agent_states
            and is_alive(agent_states[agent_id].get("sigma_phi", 0.0))
        )
        threat_signature = self.assess_threat_level(alive_agents, total_agents)

        network_context = self.form_mycelial_network(
            {"agent_states": agent_states, "agent_ids": agent_ids},
            current_pressure,
        )
        threat_signature.update(
            {
                "network_engaged": network_context["network_engaged"],
                "effective_pressure": network_context["effective_pressure"],
            }
        )

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

            guided_assessment = self.decide_action(
                assessment,
                current_pressure=network_context["effective_pressure"],
                threat_signature=threat_signature,
                network_context=network_context,
            )
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

    def decide_action(
        self,
        assessment: AgentHealth,
        *,
        current_pressure: float = 1.0,
        threat_signature: Dict[str, float] | None = None,
        network_context: Dict[str, float] | None = None,
    ) -> AgentHealth:
        """Run the planned action through the oracle before execution.

        Dynamic tolerance: acceptance widens with pressure to prevent paralysis
        under harsh environments.
        """

        threat_signature = threat_signature or {}
        network_context = network_context or {}
        effective_pressure = network_context.get("effective_pressure", current_pressure)
        lazarus_mode = bool(threat_signature.get("lazarus_mode"))
        if lazarus_mode and not self.lazarus_mode_active:
            self.lazarus_mode_active = True
            print(
                "⚠️ LAZARUS PROTOCOL ENGAGED. SHATTERING CRYSTAL FOR SURVIVAL."
            )
        elif not lazarus_mode:
            self.lazarus_mode_active = False

        context = {
            "pressure": current_pressure,
            "temperature": assessment.temperature,
        }
        contextual_resonance = self.translator.get_contextual_resonance(
            assessment.recommended_action.value, context
        )

        adjusted_assessment = assessment
        suggested_word = contextual_resonance.get("suggested_word")
        if suggested_word and suggested_word != assessment.recommended_action.value:
            adjusted_assessment = replace(
                assessment, recommended_action=CultivationAction(suggested_word)
            )

        encoded = self._encode_action_vector(adjusted_assessment)
        dream = self.inner_oracle.dream(encoded)
        resonance_state = dream.final_state
        sigma_phi_est = self._estimate_sigma_phi(resonance_state)
        global_coherence = float(np.mean(np.abs(resonance_state)))
        if network_context.get("network_engaged"):
            sigma_phi_est = float(
                np.mean([sigma_phi_est, network_context.get("mean_sigma_phi", sigma_phi_est)])
            )
            global_coherence = float(
                np.mean(
                    [
                        global_coherence,
                        network_context.get("mean_resonance_quality", global_coherence),
                    ]
                )
            )
        translation = self.translator.translate(
            sigma_phi=sigma_phi_est, global_coherence=global_coherence, frequency=1.0
        )

        base_tolerance = self.tolerance
        scaled_tolerance = base_tolerance * (1 + 0.5 * (effective_pressure - 1.0))
        acceptance_min = self.sigma_phi_target - scaled_tolerance
        acceptance_max = self.sigma_phi_target + scaled_tolerance

        veto = sigma_phi_est < acceptance_min or sigma_phi_est > acceptance_max
        survival_action = (
            adjusted_assessment.recommended_action != CultivationAction.OBSERVE
        )

        decision = "pass"
        new_action = adjusted_assessment.recommended_action
        new_strength = adjusted_assessment.action_strength
        translation_state = translation.state

        if lazarus_mode:
            veto = False
            decision = "lazarus_override"
            translation_state = "CHAOTIC_INTERVENTION"
            if network_context.get("network_engaged"):
                decision = "network_redistribution"
                translation_state = "MYCELIAL_SHIELD"
                new_action = CultivationAction.STABILIZE
                new_strength = min(1.0, max(new_strength, 0.6))
            else:
                if new_action in {
                    CultivationAction.STABILIZE,
                    CultivationAction.OBSERVE,
                }:
                    new_action = CultivationAction.RESUSCITATE
                elif new_action in {CultivationAction.COOL, CultivationAction.DAMPEN}:
                    new_action = CultivationAction.WARM

                probability_boost = 2.0
                new_strength = min(1.0, new_strength * probability_boost)
        else:
            if (
                veto
                and effective_pressure >= 4.5
                and sigma_phi_est > 0.08
                and survival_action
            ):
                veto = False

            if veto:
                decision = "veto"
                new_action = CultivationAction.OBSERVE
                new_strength = 0.0
                self.oracle_vetoes += 1
            elif translation.state == "LUCID_RESONANCE":
                decision = "resonance_boost"
                new_strength = min(1.0, adjusted_assessment.action_strength * 1.2)
                self.resonance_assists += 1
                if network_context.get("network_engaged"):
                    decision = "network_resonance"
                    translation_state = "LUCID_NETWORK"
                    new_strength = min(
                        1.0,
                        np.mean(
                            [adjusted_assessment.action_strength, new_strength]
                        ),
                    )

        if (
            network_context.get("network_engaged")
            and new_action == CultivationAction.RESUSCITATE
        ):
            decision = "network_redistribution"
            translation_state = "MYCELIAL_REDISPATCH"
            new_action = CultivationAction.STABILIZE
            new_strength = min(1.0, max(new_strength, 0.5))

        self.oracle_journal.append(
            {
                "agent_id": adjusted_assessment.agent_id,
                "proposed_action": adjusted_assessment.recommended_action.value,
                "final_action": new_action.value,
                "sigma_phi_est": sigma_phi_est,
                "coherence": global_coherence,
                "translation": translation_state,
                "decision": decision,
                "pressure_atm": current_pressure,
                "tolerance": scaled_tolerance,
                "contextual_resonance": contextual_resonance,
                "threat_signature": threat_signature,
            }
        )

        if new_action != adjusted_assessment.recommended_action or not np.isclose(
            new_strength, adjusted_assessment.action_strength
        ):
            return replace(
                adjusted_assessment,
                recommended_action=new_action,
                action_strength=new_strength,
            )

        return adjusted_assessment

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

    def assess_threat_level(self, alive_agents: int, total_agents: int) -> Dict[str, float]:
        """Assess ecosystem threat based on survival ratio."""

        if total_agents <= 0:
            return {
                "alive_agents": float(alive_agents),
                "total_agents": float(total_agents),
                "alive_ratio": 0.0,
                "lazarus_mode": False,
            }

        alive_ratio = alive_agents / total_agents
        lazarus_mode = alive_ratio < 0.5
        return {
            "alive_agents": float(alive_agents),
            "total_agents": float(total_agents),
            "alive_ratio": float(alive_ratio),
            "lazarus_mode": lazarus_mode,
        }

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

    def get_cultivation_summary(self) -> Dict[str, object]:
        """Extend base summary with network telemetry."""

        summary = super().get_cultivation_summary()
        summary.update(
            {
                "network_effective_pressure_trace": self.network_pressure_trace,
                "network_engagement_trace": self.network_engagement_trace,
                "final_effective_pressure": self.network_pressure_trace[-1]
                if self.network_pressure_trace
                else None,
            }
        )
        return summary


__all__ = ["CrystalGardener"]
