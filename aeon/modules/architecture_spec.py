"""Architecture extraction utilities and core-module contracts for Aeon."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class LayerSpec:
    key: str
    title: str
    description: str


@dataclass(frozen=True)
class CoreModuleSpec:
    name: str
    responsibility: str
    interfaces: list[str]
    cooperates_with: list[str]


_LAYER_PATTERNS = {
    "nullkern": [r"Schicht\s*0:([^\n]+)", r"\[\s*0\.\s*Nullkern\s*\]", r"###\s*\*\*1\.\s*Nullkern"],
    "aeonshell": [r"Schicht\s*1:([^\n]+)", r"\[\s*1\.\s*AeonShell\s*\]", r"###\s*\*\*2\.\s*AeonShell"],
    "agent_layer": [r"Schicht\s*2:([^\n]+)", r"\[\s*2\.\s*Agenten-Ebene\s*\]", r"###\s*\*\*3\.\s*Agenten-Ebene"],
    "physical_layer": [r"Schicht\s*3:([^\n]+)", r"\[\s*3\.\s*Physische Ebene\s*\]", r"###\s*\*\*4\.\s*Physische Ebene"],
}

CORE_MODULE_REGISTRY = sorted(
    [
        CoreModuleSpec(
            name="AeonShell",
            responsibility="Parse/generate symbolic shell statements and expose shell bus semantics.",
            interfaces=["AeonShellParser.parse", "AeonShellGenerator.generate", "AeonShell bus events"],
            cooperates_with=["MasterGPT", "CREP", "Nullkern", "UnifiedMandala"],
        ),
        CoreModuleSpec(
            name="BioGPT",
            responsibility="Translate biological observables into Aeon-compatible hypotheses.",
            interfaces=["delegate(intent='bio_analysis')", "knowledge upsert/query"],
            cooperates_with=["MasterGPT", "GenesisMath", "KnowledgeSystem"],
        ),
        CoreModuleSpec(
            name="CREP",
            responsibility="Quality gate over Coherence, Resonance, Ethics, Precision.",
            interfaces=["GenesisOrchestrator.crep_validate", "telemetry.crep_mean_score"],
            cooperates_with=["MasterGPT", "TutorGPT", "Sigillin"],
        ),
        CoreModuleSpec(
            name="CosmoGPT",
            responsibility="Provide cosmology-domain reasoning and OIPK/UTAC interpretations.",
            interfaces=["delegate(intent='cosmo_analysis')", "telemetry sigma/kappa"],
            cooperates_with=["MasterGPT", "GenesisMath", "AeonShell"],
        ),
        CoreModuleSpec(
            name="GenesisMath",
            responsibility="Formalize models, null models, and ΔAIC-style falsifiability metrics.",
            interfaces=["Nullkern.compute_aic_comparison", "Nullkern.formalize_dynamics"],
            cooperates_with=["MasterGPT", "CREP", "KnowledgeSystem"],
        ),
        CoreModuleSpec(
            name="MasterGPT",
            responsibility="Coordinate delegations across domain agents and shell interactions.",
            interfaces=["GenesisOrchestrator.delegate", "GenesisOrchestrator.broadcast"],
            cooperates_with=["TutorGPT", "CosmoGPT", "BioGPT", "CREP"],
        ),
        CoreModuleSpec(
            name="Sigillin",
            responsibility="Track meaning/shadow codex lineage and ritualized recovery links.",
            interfaces=["seed/bedeutungssigillin/*", "seed/shadow_sigillin/*", "v2_codex tri-layer"],
            cooperates_with=["CREP", "UnifiedMandala", "MasterGPT"],
        ),
        CoreModuleSpec(
            name="TutorGPT",
            responsibility="Guide pedagogical decomposition and human-verifiable explanations.",
            interfaces=["delegate(intent='tutor')", "knowledge query"],
            cooperates_with=["MasterGPT", "KnowledgeSystem", "AeonShell"],
        ),
        CoreModuleSpec(
            name="UnifiedMandala",
            responsibility="Cross-module semantic map for layer alignment and governance coupling.",
            interfaces=["layer-spec export", "core-module contract export"],
            cooperates_with=["Sigillin", "MasterGPT", "AeonShell"],
        ),
    ],
    key=lambda spec: spec.name,
)


def extract_aeon_layers(source: Path | str) -> dict[str, LayerSpec]:
    """Extract Nullkern/AeonShell/Agent/Physical layer specs from Bauplan text."""
    path = Path(source)
    text = path.read_text(encoding="utf-8")

    result: dict[str, LayerSpec] = {}
    for key, patterns in _LAYER_PATTERNS.items():
        title = ""
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                title = match.group(1).strip() if match.groups() else key
                break
        if not title:
            title = key

        section = _extract_section(text, key)
        result[key] = LayerSpec(key=key, title=title, description=section)

    return result


def _extract_section(text: str, key: str) -> str:
    heading_variants = {
        "nullkern": ["Schicht 0", "### **1. Nullkern"],
        "aeonshell": ["Schicht 1", "### **2. AeonShell"],
        "agent_layer": ["Schicht 2", "### **3. Agenten-Ebene"],
        "physical_layer": ["Schicht 3", "### **4. Physische Ebene"],
    }

    all_heads = [h for variants in heading_variants.values() for h in variants]

    start = -1
    for candidate in heading_variants[key]:
        start = text.find(candidate)
        if start >= 0:
            break
    if start < 0:
        return ""

    later_starts = [pos for h in all_heads if (pos := text.find(h)) > start]
    end = min(later_starts) if later_starts else len(text)
    snippet = text[start:end].strip()
    return snippet.split("\n", 1)[-1].strip()


def get_core_module_contracts() -> dict[str, dict[str, object]]:
    """Return serializable core-module definitions with interfaces and cooperation model."""
    return {
        spec.name: {
            "responsibility": spec.responsibility,
            "interfaces": spec.interfaces,
            "cooperates_with": spec.cooperates_with,
        }
        for spec in CORE_MODULE_REGISTRY
    }


def export_architecture_snapshot(source: Path | str) -> dict[str, object]:
    """Create a full architecture snapshot for docs/telemetry serialization."""
    layers = {k: asdict(v) for k, v in extract_aeon_layers(source).items()}
    modules = {spec.name: asdict(spec) for spec in CORE_MODULE_REGISTRY}
    return {"layers": layers, "modules": modules}
