"""Check CREP stability across Sigillin Selfmeta triplets.

Extracted from sigillin-selfmeta-check.yml's inline Python heredoc,
which broke GitHub's workflow-file YAML parser: an unindented `import`
as the first line of a `run: |` block scalar falls below the block's
established indentation, terminating it early (ScannerError: "could
not find expected ':'").
"""

import json

CREP_THRESHOLD = 0.75


def main() -> int:
    with open("docs/meta/sigillin_index.json", "r") as f:
        data = json.load(f)

    triplets = data.get("triplets", [])
    crep_values = [t.get("crep_index") for t in triplets if t.get("crep_index") is not None]

    if not crep_values:
        print("No CREP values found in triplets")
        return 0

    crep_min = min(crep_values)
    crep_max = max(crep_values)
    crep_mean = sum(crep_values) / len(crep_values)

    print("CREP Statistics:")
    print(f"  Min:  {crep_min:.3f}")
    print(f"  Max:  {crep_max:.3f}")
    print(f"  Mean: {crep_mean:.3f}")

    if crep_min < CREP_THRESHOLD:
        print(f"WARNING: CREP below threshold ({CREP_THRESHOLD})")
        print("  System may be losing coherence!")
        return 1

    print(f"CREP stable (all > {CREP_THRESHOLD})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
