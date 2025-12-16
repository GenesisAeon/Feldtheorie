#!/usr/bin/env python3
"""Add missing sigil metadata to Trilayer files with gaps."""
import json
from pathlib import Path

def add_missing_metadata():
    seed_dir = Path('/home/user/Feldtheorie/seed')

    # Mapping of file paths to suggested sigil IDs (based on context)
    sigil_mappings = {
        'CHRONOLOGY': 'feldtheorie-chronology',
        'NextVersionPlan/Claude_V2/claude_code_handoff': 'claude-code-handoff',
        'codexfeedback': 'codex-feedback',
        'papers_index': 'papers-index',
        'seed_index': 'seed-index',
        'sources_index': 'sources-index',
        'utac_v2_gap_matrix': 'utac-v2-gap-matrix',
        'sigillin/exp_aletheia': 'experiment-aletheia',
        'sigillin/feldtheorie_mandala_bundle': 'feldtheorie-mandala-bundle',
        'sigillin/implosive_recursive_feedback': 'implosive-recursive-feedback',
        'sigillin/klimakluft_beta_amplifikator': 'klimakluft-beta-amplifikator',
        'sigillin/mor_fit_methodology_v2': 'mor-fit-methodology',
        'sigillin/utac_klimakluft_process': 'utac-klimakluft-process',
        'sigillin/utac_type6_iri': 'utac-type6-iri',
        'sigillin/wolf_messing_consciousness_bridge': 'wolf-messing-consciousness-bridge',
        'socio_ecology/planetary_threshold_cartography': 'planetary-threshold-cartography',
        'theorie/hypothese_adrenalin_zeitdilatation': 'hypothese-adrenalin-zeitdilatation',
        'theory/concept_the_mirror_machine/concept_the_mirror_machine': 'concept-mirror-machine',
        'theory/entropy_geometric_waste/entropy_geometric_waste': 'entropy-geometric-waste',
        'theory/hypothese_morphological_computing/hypothese_morphological_computing': 'hypothese-morphological-computing',
        'theory/hypothese_quantum_aliasing/hypothese_quantum_aliasing': 'hypothese-quantum-aliasing',
        'validation/evidence_oxfam_wall_89percent': 'evidence-oxfam-wall-89percent',
        'validation/results_aletheia_final': 'results-aletheia-final',
        'shadow_sigillin/v3/shadow_sigillin_v3': 'shadow-sigillin-v3',
        'releases/v4.0.0-alpha_MirrorMachine/theory/entropy_geometric_waste': 'v4-entropy-geometric-waste',
        'releases/v4.0.0-alpha_MirrorMachine/theory/hypothese_morphological_computing': 'v4-hypothese-morphological-computing',
        'releases/v4.0.0-alpha_MirrorMachine/theory/hypothese_quantum_aliasing': 'v4-hypothese-quantum-aliasing',
    }

    default_version = '1.0.0'
    updated_count = 0

    for rel_path, sigil_id in sigil_mappings.items():
        json_path = seed_dir / f"{rel_path}.json"

        if not json_path.exists():
            continue

        try:
            # Load JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            modified = False

            # Add sigil if missing
            if 'meta' not in data:
                data['meta'] = {}
                modified = True

            if 'sigil' not in data.get('meta', {}):
                data['meta']['sigil'] = sigil_id
                modified = True
                print(f"✓ Added sigil '{sigil_id}' to {rel_path}")

            # Add version if missing
            if 'version' not in data.get('meta', {}):
                data['meta']['version'] = default_version
                modified = True
                print(f"✓ Added version '{default_version}' to {rel_path}")

            # Write back if modified
            if modified:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                updated_count += 1

        except Exception as e:
            print(f"✗ Error processing {rel_path}: {e}")

    print(f"\n✓ Updated {updated_count} files with missing metadata")

if __name__ == '__main__':
    add_missing_metadata()
