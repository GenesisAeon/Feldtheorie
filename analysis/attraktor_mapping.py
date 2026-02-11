"""Attraktor-Mapping: Scans repository files for AFET terms, builds a
co-occurrence graph, computes centrality metrics, and exports results.

Usage (CLI)::

    python -m analysis.attraktor_mapping [--dirs docs theory aeon analysis integration/aeon_lantern]

Outputs:
    analysis/results/attraktor_mapping.json   – metrics + edges
    analysis/plots/attraktor_graph.png        – network visualisation
    docs/emergence/attraktor_mapping.md       – human-readable report
"""
from __future__ import annotations

import json
import re
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

try:
    import networkx as nx
except ModuleNotFoundError:  # pragma: no cover - exercised in environments without networkx
    nx = None


class AttraktorGraph:
    """Minimal weighted-undirected graph used when networkx is unavailable."""

    def __init__(self) -> None:
        self._nodes: set[str] = set()
        self._edges: dict[tuple[str, str], dict[str, float]] = {}

    def __contains__(self, node: str) -> bool:
        return node in self._nodes

    @property
    def nodes(self) -> list[str]:
        return sorted(self._nodes)

    def add_node(self, node: str) -> None:
        self._nodes.add(node)

    def add_edge(self, a: str, b: str, *, weight: float = 1.0) -> None:
        key = tuple(sorted((a, b)))
        self._edges[key] = {"weight": float(weight)}
        self._nodes.update([a, b])

    def has_edge(self, a: str, b: str) -> bool:
        return tuple(sorted((a, b))) in self._edges

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return len(self._edges)

    def degree(self, node: str) -> int:
        return sum(1 for (a, b) in self._edges if node == a or node == b)

    def edges(self, data: bool = False) -> list[tuple[str, str] | tuple[str, str, dict[str, float]]]:
        if data:
            return [(a, b, payload) for (a, b), payload in sorted(self._edges.items())]
        return [(a, b) for a, b in sorted(self._edges)]

# ---------------------------------------------------------------------------
# Canonical AFET terms to detect
# ---------------------------------------------------------------------------
AFET_TERMS: list[str] = [
    "UTAC",
    "CREP",
    "Bardo-Phase",
    "Diamond Architecture",
    "β",
    "σ_Φ",
    "v_RIG",
    "AFET",
    "Nullkern",
    "Resonanzpfad",
    "Implosion",
    "Metastabilität",
    "Schwellenfeld",
    "MOR",
    "FIT",
]

# Pre-compiled patterns: each term gets a regex that matches it literally.
_TERM_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (term, re.compile(re.escape(term))) for term in AFET_TERMS
]

# File extensions to scan
_SCAN_EXTENSIONS: frozenset[str] = frozenset(
    {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".rst"}
)


# ---------------------------------------------------------------------------
# Term extraction
# ---------------------------------------------------------------------------

def extract_terms_from_text(text: str) -> list[str]:
    """Return deduplicated list of AFET terms found in *text*."""
    found: list[str] = []
    seen: set[str] = set()
    for term, pattern in _TERM_PATTERNS:
        if term not in seen and pattern.search(text):
            found.append(term)
            seen.add(term)
    return found


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------

def scan_files(directories: list[Path]) -> list[dict[str, Any]]:
    """Walk *directories*, extract terms from each eligible file.

    Returns a list of ``{"file": str, "terms": list[str]}`` dicts.
    """
    results: list[dict[str, Any]] = []
    for directory in directories:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.suffix not in _SCAN_EXTENSIONS:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            terms = extract_terms_from_text(text)
            if terms:
                results.append({"file": str(path), "terms": terms})
    return results


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_cooccurrence_graph(
    scan_results: list[dict[str, Any]],
) -> Any:
    """Build a weighted co-occurrence graph from scan results.

    Each AFET term becomes a node.  Two terms sharing a document get an
    edge whose weight equals the number of documents in which they co-occur.
    """
    graph: Any = nx.Graph() if nx is not None else AttraktorGraph()
    edge_counts: Counter[tuple[str, str]] = Counter()

    for entry in scan_results:
        terms = sorted(set(entry["terms"]))
        for t in terms:
            if t not in graph:
                graph.add_node(t)
        for a, b in combinations(terms, 2):
            edge_counts[(a, b)] += 1

    for (a, b), weight in edge_counts.items():
        graph.add_edge(a, b, weight=weight)

    return graph


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_graph_metrics(graph: Any) -> dict[str, dict[str, float]]:
    """Compute degree, betweenness centrality, and PageRank for each node."""
    if graph.number_of_nodes() == 0:
        return {}

    if nx is not None:
        betweenness = nx.betweenness_centrality(graph, weight="weight")
        pagerank = nx.pagerank(graph, weight="weight")
    else:
        total_degree = sum(graph.degree(node) for node in graph.nodes)
        pagerank = {
            node: (graph.degree(node) / total_degree if total_degree > 0 else 0.0)
            for node in graph.nodes
        }
        betweenness = {node: 0.0 for node in graph.nodes}

    metrics: dict[str, dict[str, float]] = {}
    for node in graph.nodes:
        metrics[node] = {
            "degree": float(graph.degree(node)),
            "betweenness": betweenness.get(node, 0.0),
            "pagerank": pagerank.get(node, 0.0),
        }
    return metrics


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def export_json(
    metrics: dict[str, dict[str, float]],
    graph: Any,
    output_path: Path,
) -> None:
    """Write metrics and edge list to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "nodes": metrics,
        "edges": [
            {"source": u, "target": v, "weight": d.get("weight", 1)}
            for u, v, d in graph.edges(data=True)
        ],
    }
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def export_plot(graph: Any, metrics: dict[str, dict[str, float]], output_path: Path) -> None:
    """Render the co-occurrence graph to a PNG file."""
    if nx is None:
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(graph, seed=42, k=2.0)

    # Node sizes proportional to PageRank
    pr_values = [metrics.get(n, {}).get("pagerank", 0.01) for n in graph.nodes]
    max_pr = max(pr_values) if pr_values else 1.0
    node_sizes = [300 + 2000 * (v / max_pr) for v in pr_values]

    # Edge widths proportional to weight
    weights = [d.get("weight", 1) for _, _, d in graph.edges(data=True)]
    max_w = max(weights) if weights else 1
    edge_widths = [1 + 3 * (w / max_w) for w in weights]

    nx.draw_networkx_edges(graph, pos, ax=ax, width=edge_widths, alpha=0.4)
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_size=node_sizes, node_color="#4a90d9", alpha=0.8)
    nx.draw_networkx_labels(graph, pos, ax=ax, font_size=9, font_weight="bold")

    ax.set_title("AFET Attraktor-Netzwerk (Co-Occurrence)", fontsize=14)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def generate_report(
    metrics: dict[str, dict[str, float]],
    graph: Any,
    scan_results: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Generate a Markdown report at *output_path*."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ranked = sorted(metrics.items(), key=lambda kv: kv[1]["pagerank"], reverse=True)
    total_files = len(scan_results)

    lines: list[str] = [
        "# Attraktor-Mapping Report",
        "",
        f"Analysed **{total_files}** files containing AFET terminology.",
        f"Graph: **{graph.number_of_nodes()}** nodes, **{graph.number_of_edges()}** edges.",
        "",
        "## Top Attraktoren (by PageRank)",
        "",
        "| Rank | Term | PageRank | Degree | Betweenness |",
        "|------|------|----------|--------|-------------|",
    ]
    for i, (term, m) in enumerate(ranked[:15], 1):
        lines.append(
            f"| {i} | {term} | {m['pagerank']:.4f} | {m['degree']:.0f} | {m['betweenness']:.4f} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "Nodes with high PageRank and betweenness centrality act as **structural attractors**"
        " in the AFET concept space. These terms bridge multiple sub-domains and stabilise"
        " the emergent vocabulary.",
        "",
        "See `analysis/results/attraktor_mapping.json` for raw data and"
        " `analysis/plots/attraktor_graph.png` for the network visualisation.",
    ]

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

_DEFAULT_DIRS = ["docs", "theory", "aeon", "analysis", "integration/aeon_lantern"]


def main(root: Path | None = None, dirs: list[str] | None = None) -> None:
    """Run the full attraktor-mapping pipeline."""
    root = root or Path(__file__).resolve().parent.parent
    scan_dirs = [root / d for d in (dirs or _DEFAULT_DIRS)]

    scan_results = scan_files(scan_dirs)
    graph = build_cooccurrence_graph(scan_results)
    metrics = compute_graph_metrics(graph)

    export_json(metrics, graph, root / "analysis" / "results" / "attraktor_mapping.json")
    export_plot(graph, metrics, root / "analysis" / "plots" / "attraktor_graph.png")
    generate_report(metrics, graph, scan_results, root / "docs" / "emergence" / "attraktor_mapping.md")

    print(f"Attraktor-Mapping complete: {graph.number_of_nodes()} terms, {graph.number_of_edges()} edges.")


if __name__ == "__main__":
    main()
