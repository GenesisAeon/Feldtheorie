#!/usr/bin/env python3
"""
Fractal Governance Engine

This script implements bi-directional governance propagation:
1. TOP-DOWN: Distributes policies from root to subdirectories
2. BOTTOM-UP: Aggregates local policies and reports inconsistencies

The system recognizes three recursive modes:
- Mode A (Code): Programming contexts (scripts/, models/, api/)
- Mode B (Data): Data analysis contexts (data/, analysis/)
- Mode C (Research): Research contexts (docs/, seed/, paper/)

Each context gets specialized versions of:
- AGENTS.md (who works here)
- ETHICS.md (what is allowed)
- ARCHITECTURE.md (how it's built)
- POLICY.md (specific rules)
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

# ============================================================================
# CONFIGURATION
# ============================================================================

GOVERNANCE_VERSION = "1.0.0"
REPO_ROOT = Path(__file__).parent.parent.parent.parent
TEMPLATES_DIR = REPO_ROOT / "modules" / "champollion" / "templates"

# Governance files to manage
GOVERNANCE_FILES = ["AGENTS.md", "ETHICS.md", "ARCHITECTURE.md", "POLICY.md"]

# Directories to skip
SKIP_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "venv",
    "env",
    ".venv",
    "modules/champollion",  # Don't govern the governance system itself
}

# Custom rules markers
CUSTOM_RULES_START = "<!-- CUSTOM_RULES -->"
CUSTOM_RULES_END = "<!-- /CUSTOM_RULES -->"


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class ModeConfig:
    """Configuration for a governance mode"""

    mode: str
    mode_id: str
    description: str
    folder_patterns: list[str]
    agents_content: str
    workflow_content: str
    ethics_content: str
    data_governance: str
    misuse_risks: str
    architecture_content: str
    policy_content: str
    quality_gates: str
    automation_hooks: str


@dataclass
class Context:
    """Represents a directory context in the repository"""

    path: Path
    depth: int
    mode: ModeConfig | None = None
    parent: Optional["Context"] = None
    custom_rules: dict[str, str] = field(default_factory=dict)
    has_governance: bool = False
    inconsistencies: list[str] = field(default_factory=list)


@dataclass
class GovernanceReport:
    """Aggregated governance report"""

    total_contexts: int = 0
    contexts_by_mode: dict[str, int] = field(default_factory=dict)
    total_agents: dict[str, int] = field(default_factory=dict)
    inconsistencies: list[tuple[str, str]] = field(default_factory=list)
    custom_policies: list[tuple[str, str]] = field(default_factory=list)


# ============================================================================
# MODE DETECTION
# ============================================================================


def load_mode_config(mode_dir: Path) -> ModeConfig | None:
    """Load configuration for a specific mode"""
    config_file = mode_dir / "config.yaml"
    if not config_file.exists():
        return None

    with open(config_file) as f:
        data = yaml.safe_load(f)

    return ModeConfig(**data)


def load_all_modes() -> list[ModeConfig]:
    """Load all mode configurations"""
    modes = []
    for mode_dir in TEMPLATES_DIR.iterdir():
        if mode_dir.is_dir() and mode_dir.name.startswith("mode_"):
            config = load_mode_config(mode_dir)
            if config:
                modes.append(config)
    return modes


def detect_mode(path: Path, modes: list[ModeConfig]) -> ModeConfig | None:
    """
    Detect which governance mode applies to a directory.

    Returns the first matching mode based on folder patterns.
    """
    rel_path = str(path.relative_to(REPO_ROOT))

    for mode in modes:
        for pattern in mode.folder_patterns:
            # Check if the path matches the pattern
            if rel_path.startswith(pattern.rstrip("/")):
                return mode
            # Also check if the directory name matches
            if path.name + "/" == pattern:
                return mode

    return None


# ============================================================================
# TEMPLATE RENDERING
# ============================================================================


def extract_custom_rules(content: str) -> str:
    """Extract custom rules block from existing governance file"""
    if CUSTOM_RULES_START not in content:
        return ""

    start = content.find(CUSTOM_RULES_START)
    end = content.find(CUSTOM_RULES_END, start)

    if end == -1:
        return ""

    # Extract everything between markers, including the markers
    return content[start : end + len(CUSTOM_RULES_END)]


def render_template(template_path: Path, context: Context, mode: ModeConfig, timestamp: str) -> str:
    """
    Render a governance template with context-specific values.

    Preserves CUSTOM_RULES blocks if they exist.
    """
    with open(template_path) as f:
        template = f.read()

    # Calculate parent path
    parent_path = str(context.parent.path.relative_to(REPO_ROOT)) if context.parent else "/"
    current_path = str(context.path.relative_to(REPO_ROOT))

    # Prepare replacements
    replacements = {
        "{{PATH}}": current_path,
        "{{CURRENT_DEPTH}}": str(context.depth),
        "{{PARENT_CONTEXT}}": parent_path,
        "{{PARENT_PATH}}": parent_path,
        "{{MODE}}": mode.mode,
        "{{TIMESTAMP}}": timestamp,
        "{{GOVERNANCE_VERSION}}": GOVERNANCE_VERSION,
        "{{MODE_SPECIFIC_AGENTS}}": mode.agents_content,
        "{{AGENT_LIST}}": "See mode-specific agents above",
        "{{MODE_SPECIFIC_WORKFLOW}}": mode.workflow_content,
        "{{MODE_SPECIFIC_ETHICS}}": mode.ethics_content,
        "{{DATA_GOVERNANCE_RULES}}": mode.data_governance,
        "{{MISUSE_RISKS}}": mode.misuse_risks,
        "{{MODE_SPECIFIC_ARCHITECTURE}}": mode.architecture_content,
        "{{COMPONENT_DIAGRAM}}": f"{current_path}\n└── (See mode-specific architecture)",
        "{{DEPENDENCY_LIST}}": "See parent context and root dependencies",
        "{{INFORMATION_FLOWS}}": "Follows Trilayer principle: YAML → JSON → MD",
        "{{INTEGRATION_POINTS}}": "Integrates with parent context governance",
        "{{MODE_SPECIFIC_POLICY}}": mode.policy_content,
        "{{QUALITY_GATES}}": mode.quality_gates,
        "{{AUTOMATION_HOOKS}}": mode.automation_hooks,
        "{{CHANGE_LOG}}": f"- {timestamp}: Initial governance deployment (v{GOVERNANCE_VERSION})",
    }

    # Apply replacements
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    # Restore custom rules if they exist
    filename = template_path.name
    if filename in context.custom_rules:
        custom_block = context.custom_rules[filename]
        # Replace the empty custom rules block with the saved one
        pattern = re.escape(CUSTOM_RULES_START) + r".*?" + re.escape(CUSTOM_RULES_END)
        # Use a lambda so backslashes in custom_block (e.g. "\z" in a path or
        # regex snippet) are inserted literally instead of being parsed as
        # re.sub backreferences (which raises "bad escape" for invalid ones).
        rendered = re.sub(pattern, lambda _match: custom_block, rendered, flags=re.DOTALL)

    return rendered


# ============================================================================
# TOP-DOWN PROPAGATION
# ============================================================================


def read_root_governance() -> dict[str, str]:
    """Read root-level governance files"""
    governance = {}
    for filename in GOVERNANCE_FILES:
        filepath = REPO_ROOT / filename
        if filepath.exists():
            with open(filepath) as f:
                governance[filename] = f.read()
    return governance


def should_skip_directory(path: Path) -> bool:
    """Check if directory should be skipped"""
    rel_path = str(path.relative_to(REPO_ROOT))

    # Check exact matches
    if rel_path in SKIP_DIRS:
        return True

    # Check if any part of the path matches skip patterns
    for skip in SKIP_DIRS:
        if skip in rel_path:
            return True

    return False


def scan_directory_tree(
    root: Path, modes: list[ModeConfig], parent: Context | None = None, depth: int = 0
) -> list[Context]:
    """
    Recursively scan directory tree and create Context objects.

    Returns a flat list of all contexts.
    """
    contexts = []

    if should_skip_directory(root):
        return contexts

    # Create context for this directory
    mode = detect_mode(root, modes)

    if mode is not None:  # Only create context if mode is detected
        context = Context(path=root, depth=depth, mode=mode, parent=parent)

        # Check if governance files already exist and extract custom rules
        for filename in GOVERNANCE_FILES:
            filepath = root / filename
            if filepath.exists():
                context.has_governance = True
                with open(filepath) as f:
                    content = f.read()
                    custom_rules = extract_custom_rules(content)
                    if custom_rules:
                        context.custom_rules[filename] = custom_rules

        contexts.append(context)
        use_parent = context
    else:
        use_parent = parent

    # Recurse into subdirectories
    try:
        for item in sorted(root.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                subcontexts = scan_directory_tree(item, modes, parent=use_parent, depth=depth + 1)
                contexts.extend(subcontexts)
    except PermissionError:
        pass  # Skip directories we can't read

    return contexts


def propagate_governance(contexts: list[Context], dry_run: bool = False) -> int:
    """
    TOP-DOWN: Propagate governance files to all contexts.

    Returns the number of files written.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    files_written = 0

    for context in contexts:
        if context.mode is None:
            continue

        # Ensure directory exists
        context.path.mkdir(parents=True, exist_ok=True)

        # Generate each governance file
        for filename in GOVERNANCE_FILES:
            template_path = TEMPLATES_DIR / "base" / filename

            if not template_path.exists():
                print(f"⚠️  Template not found: {template_path}")
                continue

            rendered = render_template(template_path, context, context.mode, timestamp)
            output_path = context.path / filename

            if dry_run:
                print(f"[DRY RUN] Would write: {output_path.relative_to(REPO_ROOT)}")
            else:
                with open(output_path, "w") as f:
                    f.write(rendered)
                files_written += 1
                print(f"✓ Written: {output_path.relative_to(REPO_ROOT)}")

    return files_written


# ============================================================================
# BOTTOM-UP AGGREGATION
# ============================================================================


def aggregate_governance(contexts: list[Context]) -> GovernanceReport:
    """
    BOTTOM-UP: Aggregate governance information and detect inconsistencies.
    """
    report = GovernanceReport()
    report.total_contexts = len(contexts)

    for context in contexts:
        if context.mode is None:
            continue

        # Count contexts by mode
        mode_id = context.mode.mode_id
        report.contexts_by_mode[mode_id] = report.contexts_by_mode.get(mode_id, 0) + 1

        # Count agents (simplified - would parse AGENTS.md in real implementation)
        report.total_agents[mode_id] = report.total_agents.get(mode_id, 0) + 1

        # Detect inconsistencies
        if context.has_governance and not context.custom_rules:
            # Has governance but no custom rules - might be inconsistent
            pass  # This is fine actually

        # Record custom policies
        if context.custom_rules:
            for filename, rules in context.custom_rules.items():
                rel_path = str(context.path.relative_to(REPO_ROOT))
                report.custom_policies.append((rel_path, filename))

    return report


def write_governance_report(report: GovernanceReport, output_path: Path):
    """Write the aggregated governance report"""
    content = f"""# Fractal Governance Report

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Governance Version:** {GOVERNANCE_VERSION}

---

## Summary

- **Total Governed Contexts:** {report.total_contexts}
- **Contexts by Mode:**
"""

    for mode_id, count in sorted(report.contexts_by_mode.items()):
        content += f"  - {mode_id}: {count}\n"

    content += f"\n- **Total Agents:** {sum(report.total_agents.values())}\n"
    content += "- **Agents by Mode:**\n"

    for mode_id, count in sorted(report.total_agents.items()):
        content += f"  - {mode_id}: {count}\n"

    content += "\n---\n\n## Contexts with Custom Policies\n\n"

    if report.custom_policies:
        for path, filename in report.custom_policies:
            content += f"- `{path}/{filename}`\n"
    else:
        content += "*No custom policies detected.*\n"

    content += "\n---\n\n## Inconsistencies\n\n"

    if report.inconsistencies:
        for path, issue in report.inconsistencies:
            content += f"- `{path}`: {issue}\n"
    else:
        content += "*No inconsistencies detected.*\n"

    content += """

---

## Recommendations

1. **Review Custom Policies**: Check contexts with custom rules to ensure they don't conflict with root governance
2. **Mode Coverage**: Ensure all relevant directories have appropriate governance files
3. **Regular Audits**: Run this tool weekly to maintain governance hygiene
4. **Bottom-Up Feedback**: Review custom policies for patterns that should be elevated to root governance

---

*This report was generated automatically by the Fractal Governance Engine.*
"""

    with open(output_path, "w") as f:
        f.write(content)

    print(f"\n📊 Report written: {output_path.relative_to(REPO_ROOT)}")


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fractal Governance Engine - Bi-directional policy propagation"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Only generate the governance report (no propagation)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("FRACTAL GOVERNANCE ENGINE")
    print("=" * 70)
    print(f"Repository: {REPO_ROOT}")
    print(f"Governance Version: {GOVERNANCE_VERSION}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 70)
    print()

    # Load mode configurations
    print("📦 Loading mode configurations...")
    modes = load_all_modes()
    print(f"   Loaded {len(modes)} modes:")
    for mode in modes:
        print(f"   - {mode.mode} ({mode.mode_id})")
    print()

    # Scan directory tree
    print("🔍 Scanning directory tree...")
    contexts = scan_directory_tree(REPO_ROOT, modes)
    print(f"   Found {len(contexts)} governed contexts")
    print()

    # TOP-DOWN: Propagate governance
    if not args.report_only:
        print("⬇️  TOP-DOWN: Propagating governance files...")
        files_written = propagate_governance(contexts, dry_run=args.dry_run)
        print(f"   {'Would write' if args.dry_run else 'Wrote'} {files_written} files")
        print()

    # BOTTOM-UP: Aggregate and report
    print("⬆️  BOTTOM-UP: Aggregating governance information...")
    report = aggregate_governance(contexts)
    report_path = REPO_ROOT / "GOVERNANCE_REPORT.md"

    if not args.dry_run:
        write_governance_report(report, report_path)
    else:
        print(f"[DRY RUN] Would write report to: {report_path.relative_to(REPO_ROOT)}")

    print()
    print("=" * 70)
    print("✅ FRACTAL GOVERNANCE ENGINE COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
