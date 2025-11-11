# CREP Parser - Sigillin→Codex Automation

**Version:** 2.0 (with --write-codex)
**Updated:** 2025-11-11

## Overview

`crep_parser.py` parses Sigillin YAML files, validates their structure, and can automatically write them to `seed/codexfeedback.*` (Trilayer: YAML + JSON + MD).

## Usage

### Basic Parsing (JSON Output)

```bash
python scripts/crep_parser.py --examples --validate
```

### Write to Codex (Automation!)

```bash
python scripts/crep_parser.py --examples --validate --write-codex
```

This will:
1. Parse all Sigillin YAML files
2. Convert them to codex entry format
3. Append them to `seed/codexfeedback.yaml`, `.json`, and `.md` (Trilayer!)
4. Update metadata timestamps
5. Check for ID collisions (skips duplicates)

### Custom Codex Directory

```bash
python scripts/crep_parser.py -d my/sigillins --write-codex --codex-dir my/codex
```

## Flags

- `--examples`: Parse canonical examples from `seed/sigillin/examples/`
- `-d DIR, --directory DIR`: Parse YAML files from directory
- `files...`: Explicit Sigillin files to parse
- `--validate`: Enforce schema constraints (β ≥ 0.5, CREP ∈ [0,1], etc.)
- `-o OUTPUT, --output OUTPUT`: Write JSON summary to file (default: stdout)
- **`--write-codex`**: Write parsed Sigillins to codex (NEW!)
- **`--codex-dir DIR`**: Codex directory (default: `seed/`)

## Sigillin→Codex Mapping

| Sigillin Field | Codex Field |
|----------------|-------------|
| `core.id` | `id` (prefixed with "sigil-") |
| `core.title` | `title` |
| `core.status` | `status` |
| `logistic_frame.beta` | `parameters.beta` |
| `logistic_frame.Theta` | `parameters.Theta` |
| `logistic_frame.R` | `parameters.R` |
| `tri_layer.formal` | `notes.formal` |
| `tri_layer.empirical` | `notes.empirical` |
| `tri_layer.poetic` | `notes.poetic` |
| `crep` | (in `resonance` description) |
| `path` | `scope` |

## ID Collision Handling

If a Sigillin ID already exists in the codex, the parser will:
- Print a warning
- Skip that entry
- Continue with non-colliding entries

## Example Output

```
✅ Added 4 entries to codex (Trilayer: YAML, JSON, MD)
   - sigil-B-021: Codex Resonance Ledger
   - sigil-D-014: Threshold Sandbox Sweep
   - sigil-F-005: β Outlier Vigil
   - sigil-O-001: Seed-Orbit Navigation
```

## Error Handling

- **Missing codex files**: Returns error if `codexfeedback.yaml` or `.json` not found
- **Validation errors**: Returns error if schema constraints violated (when `--validate` used)
- **Write errors**: Returns error if Trilayer write fails

## Trilayer Consistency

The parser maintains Trilayer consistency by:
1. Loading existing YAML & JSON
2. Appending new entries to both
3. Generating fresh MD from updated YAML
4. Writing all 3 formats atomically

## Code Structure

```
scripts/crep_parser.py (477 LOC)
├── Parsing Functions (lines 1-220)
│   ├── load_yaml()
│   ├── validate_structure()
│   ├── validate_semantics()
│   └── parse_sigils()
├── Codex Integration (lines 253-424, NEW!)
│   ├── sigil_to_codex_entry()
│   ├── load_codex_trilayer()
│   ├── write_codex_trilayer()
│   ├── generate_codex_markdown()
│   └── append_to_codex()
├── CLI (lines 425-460)
│   ├── create_argument_parser() [updated with --write-codex]
│   └── main() [updated with codex logic]
└── Entry Point (lines 476-477)
```

## Related Files

- `seed/codexfeedback.yaml` - YAML codex (target for --write-codex)
- `seed/codexfeedback.json` - JSON codex (updated in parallel)
- `seed/codexfeedback.md` - Markdown codex (regenerated from YAML)
- `seed/sigillin/examples/*.yaml` - Example Sigillin files

## Roadmap Integration

This feature completes **v2-feat-auto-002** (Parser→Codex Automation).

**Gap Code:** `sys-shadow-002` (Codex violations) → **RESOLVED**

---

**Version:** 2.0 (with --write-codex)
**Codex:** v2-pr-0019
**Maintained by:** Claude Code + Johann Römer

*"From Sigillin to Codex - automated coherence!"* 🌀✨
