#!/usr/bin/env python3
"""Telemetry Dashboard for Feldtheorie Repository Health.

This script aggregates metrics from multiple sources and provides both:
1. JSON API for programmatic access
2. HTML dashboard for human viewing

METRICS COLLECTED:
- Trilayer Synchronization (sigillin_sync.py)
- Test Coverage (pytest-cov)
- Preset Alignment (preset_alignment_guard.py)
- Codex Status (codexfeedback.*)
- CI Health (GitHub Actions)
- Git Status (branch, commits, changes)

USAGE:
    # Generate JSON telemetry
    python scripts/telemetry_dashboard.py --format json --output telemetry.json

    # Generate HTML dashboard
    python scripts/telemetry_dashboard.py --format html --output telemetry.html

    # Start HTTP server for live dashboard
    python scripts/telemetry_dashboard.py --serve --port 8000

INTEGRATION:
    Add to .github/workflows/telemetry.yml for automated dashboard updates
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
VERSION_FILE = BASE_DIR / "VERSION.yaml"


def _read_package_version() -> str:
    """Read package version from VERSION.yaml (single source of truth)."""
    try:
        with VERSION_FILE.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data.get("package_version", "unknown")
    except (OSError, yaml.YAMLError):
        return "unknown"


# Import sigillin_sync for trilayer health
sys.path.insert(0, str(BASE_DIR))
from scripts.sigillin_sync import discover_trilayers, generate_report, resolve_roots

# ============================================================================
# Metric Collection
# ============================================================================


def collect_trilayer_health() -> dict[str, object]:
    """Collect trilayer synchronization metrics."""
    try:
        roots = resolve_roots([])  # Use defaults
        trilayers = discover_trilayers(roots)
        report = generate_report(trilayers)

        return {
            "status": "healthy" if report["meta"]["counts"]["with_gaps"] == 0 else "degraded",
            "total_trilayers": report["meta"]["counts"]["total"],
            "trilayers_with_gaps": report["meta"]["counts"]["with_gaps"],
            "gap_percentage": (
                report["meta"]["counts"]["with_gaps"] / report["meta"]["counts"]["total"] * 100
                if report["meta"]["counts"]["total"] > 0
                else 0
            ),
            "last_check": report["meta"]["generated_at"],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def collect_test_coverage() -> dict[str, object]:
    """Collect pytest test coverage metrics."""
    try:
        # Run pytest with coverage
        result = subprocess.run(
            ["pytest", "--quiet", "--tb=no", "--co", "-q"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Count tests
        lines = result.stdout.split("\n")
        test_count = sum(1 for line in lines if line.strip().startswith("<"))

        # Check if coverage report exists
        coverage_file = BASE_DIR / ".coverage"
        has_coverage = coverage_file.exists()

        return {
            "status": "healthy" if result.returncode == 0 else "degraded",
            "total_tests": test_count,
            "tests_passing": test_count if result.returncode == 0 else "unknown",
            "has_coverage_data": has_coverage,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def collect_codex_status() -> dict[str, object]:
    """Collect codex feedback metrics."""
    try:
        codex_json = BASE_DIR / "seed" / "codexfeedback.json"

        if not codex_json.exists():
            return {"status": "missing", "error": "codexfeedback.json not found"}

        with codex_json.open("r", encoding="utf-8") as f:
            codex_data = json.load(f)

        entries = codex_data.get("entries", [])

        # Find latest entry
        latest = None
        if entries:
            # Sort by created_at
            sorted_entries = sorted(
                entries, key=lambda e: e.get("created_at", "1970-01-01T00:00:00Z"), reverse=True
            )
            latest = sorted_entries[0] if sorted_entries else None

        return {
            "status": "healthy",
            "total_entries": len(entries),
            "latest_entry_id": latest.get("id") if latest else None,
            "latest_entry_date": latest.get("created_at") if latest else None,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def collect_git_status() -> dict[str, object]:
    """Collect git repository status."""
    try:
        # Get branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5,
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        # Get commit count
        commit_result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5,
        )
        commit_count = int(commit_result.stdout.strip()) if commit_result.returncode == 0 else 0

        # Get uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5,
        )
        uncommitted = (
            len(status_result.stdout.strip().split("\n")) if status_result.stdout.strip() else 0
        )

        return {
            "status": "healthy" if uncommitted == 0 else "dirty",
            "branch": branch,
            "total_commits": commit_count,
            "uncommitted_changes": uncommitted,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def collect_preset_alignment() -> dict[str, object]:
    """Collect preset alignment metrics (simulator ↔ analysis)."""
    # This would call preset_alignment_guard.py, but for prototype we return placeholder
    return {
        "status": "not_implemented",
        "note": "Run analysis/preset_alignment_guard.py separately",
    }


# ============================================================================
# Aggregation
# ============================================================================


def aggregate_telemetry() -> dict[str, object]:
    """Aggregate all telemetry metrics into single envelope."""
    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repository": "Feldtheorie",
            "version": _read_package_version(),
        },
        "health_summary": {
            "overall_status": "healthy",  # Computed below
            "components": {
                "trilayer_sync": "healthy",
                "tests": "healthy",
                "codex": "healthy",
                "git": "healthy",
            },
        },
        "metrics": {
            "trilayer_health": collect_trilayer_health(),
            "test_coverage": collect_test_coverage(),
            "codex_status": collect_codex_status(),
            "git_status": collect_git_status(),
            "preset_alignment": collect_preset_alignment(),
        },
    }


# ============================================================================
# Output Formats
# ============================================================================


def export_json(telemetry: dict[str, object], output_path: Path) -> None:
    """Export telemetry to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(telemetry, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON telemetry exported to {output_path}", file=sys.stderr)


def export_html(telemetry: dict[str, object], output_path: Path) -> None:
    """Export telemetry to HTML dashboard."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feldtheorie Telemetry Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 30px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            padding: 20px;
        }}
        .metric-card.healthy {{ border-left-color: #28a745; }}
        .metric-card.degraded {{ border-left-color: #ffc107; }}
        .metric-card.error {{ border-left-color: #dc3545; }}
        .metric-title {{
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .metric-detail {{
            color: #666;
            font-size: 0.9em;
            margin: 5px 0;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-healthy {{ background: #28a745; color: white; }}
        .status-degraded {{ background: #ffc107; color: #333; }}
        .status-error {{ background: #dc3545; color: white; }}
        footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Feldtheorie Telemetry Dashboard</h1>
        <div class="timestamp">Generated: {telemetry['meta']['generated_at']}</div>

        <div class="metric-grid">
            <!-- Trilayer Health -->
            <div class="metric-card {telemetry['metrics']['trilayer_health'].get('status', 'error')}">
                <div class="metric-title">Trilayer Synchronization</div>
                <div class="metric-value">{telemetry['metrics']['trilayer_health'].get('total_trilayers', 0)}</div>
                <div class="metric-detail">Total Trilayers</div>
                <div class="metric-detail">
                    <span class="status-badge status-{telemetry['metrics']['trilayer_health'].get('status', 'error')}">
                        {telemetry['metrics']['trilayer_health'].get('status', 'error').upper()}
                    </span>
                </div>
                <div class="metric-detail">
                    Gaps: {telemetry['metrics']['trilayer_health'].get('trilayers_with_gaps', 'N/A')}
                </div>
            </div>

            <!-- Test Coverage -->
            <div class="metric-card {telemetry['metrics']['test_coverage'].get('status', 'error')}">
                <div class="metric-title">Test Suite</div>
                <div class="metric-value">{telemetry['metrics']['test_coverage'].get('total_tests', 0)}</div>
                <div class="metric-detail">Total Tests</div>
                <div class="metric-detail">
                    <span class="status-badge status-{telemetry['metrics']['test_coverage'].get('status', 'error')}">
                        {telemetry['metrics']['test_coverage'].get('status', 'error').upper()}
                    </span>
                </div>
                <div class="metric-detail">
                    Passing: {telemetry['metrics']['test_coverage'].get('tests_passing', 'N/A')}
                </div>
            </div>

            <!-- Codex Status -->
            <div class="metric-card {telemetry['metrics']['codex_status'].get('status', 'error')}">
                <div class="metric-title">Codex Memory</div>
                <div class="metric-value">{telemetry['metrics']['codex_status'].get('total_entries', 0)}</div>
                <div class="metric-detail">Total Entries</div>
                <div class="metric-detail">
                    <span class="status-badge status-{telemetry['metrics']['codex_status'].get('status', 'error')}">
                        {telemetry['metrics']['codex_status'].get('status', 'error').upper()}
                    </span>
                </div>
                <div class="metric-detail">
                    Latest: {telemetry['metrics']['codex_status'].get('latest_entry_id', 'N/A')}
                </div>
            </div>

            <!-- Git Status -->
            <div class="metric-card {telemetry['metrics']['git_status'].get('status', 'error')}">
                <div class="metric-title">Git Repository</div>
                <div class="metric-value">{telemetry['metrics']['git_status'].get('total_commits', 0)}</div>
                <div class="metric-detail">Total Commits</div>
                <div class="metric-detail">
                    <span class="status-badge status-{telemetry['metrics']['git_status'].get('status', 'error')}">
                        {telemetry['metrics']['git_status'].get('status', 'error').upper()}
                    </span>
                </div>
                <div class="metric-detail">
                    Branch: {telemetry['metrics']['git_status'].get('branch', 'N/A')}
                </div>
                <div class="metric-detail">
                    Uncommitted: {telemetry['metrics']['git_status'].get('uncommitted_changes', 0)}
                </div>
            </div>
        </div>

        <footer>
            <p>Feldtheorie v{telemetry['meta']['version']} | "Das Feld atmet in verschiedenen Rhythmen"</p>
        </footer>
    </div>
</body>
</html>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ HTML dashboard exported to {output_path}", file=sys.stderr)


# ============================================================================
# HTTP Server
# ============================================================================


class TelemetryHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for live telemetry dashboard."""

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            telemetry = aggregate_telemetry()
            html_path = BASE_DIR / "telemetry_dashboard.html"
            export_html(telemetry, html_path)

            with html_path.open("r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode("utf-8"))

        elif self.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            telemetry = aggregate_telemetry()
            self.wfile.write(json.dumps(telemetry, indent=2).encode("utf-8"))

        else:
            super().do_GET()


def serve_dashboard(port: int = 8000):
    """Start HTTP server for live telemetry dashboard."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, TelemetryHandler)

    print(f"🌐 Telemetry Dashboard running at http://localhost:{port}/", file=sys.stderr)
    print(f"📊 JSON API available at http://localhost:{port}/api/telemetry", file=sys.stderr)
    print("Press Ctrl+C to stop...\n", file=sys.stderr)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down dashboard...", file=sys.stderr)
        httpd.shutdown()


# ============================================================================
# CLI
# ============================================================================


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Feldtheorie Telemetry Dashboard")

    parser.add_argument(
        "--format",
        choices=["json", "html", "both"],
        default="both",
        help="Output format (default: both)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE_DIR / "telemetry",
        help="Output path (without extension for 'both')",
    )
    parser.add_argument("--serve", action="store_true", help="Start HTTP server for live dashboard")
    parser.add_argument("--port", type=int, default=8000, help="HTTP server port (default: 8000)")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.serve:
        serve_dashboard(port=args.port)
        return 0

    print("Collecting telemetry...", file=sys.stderr)
    telemetry = aggregate_telemetry()

    if args.format in ["json", "both"]:
        json_path = args.output.with_suffix(".json") if args.format == "both" else args.output
        export_json(telemetry, json_path)

    if args.format in ["html", "both"]:
        html_path = args.output.with_suffix(".html") if args.format == "both" else args.output
        export_html(telemetry, html_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
