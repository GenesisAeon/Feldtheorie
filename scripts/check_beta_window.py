"""Check beta-window compliance across Sigillin Selfmeta triplets.

Extracted from sigillin-selfmeta-check.yml's inline Python heredoc for
the same reason as check_crep_stability.py: the unindented heredoc
body broke GitHub's workflow-file YAML parser.
"""

import json


def main() -> int:
    with open("docs/meta/sigillin_index.json", "r") as f:
        data = json.load(f)

    triplets = data.get("triplets", [])
    beta_windows = [t.get("beta_window") for t in triplets if t.get("beta_window") is not None]

    if not beta_windows:
        print("No beta-windows found in triplets")
        return 0

    print("Beta-Window Analysis:")

    for t in triplets:
        window = t.get("beta_window")
        if not window:
            continue
        sigil_id = t.get("sigil_id", "unknown")
        print(f"  {sigil_id}: beta in {window}")

        if not isinstance(window, list) or len(window) != 2:
            print("    Invalid beta-window format")
            return 1

        beta_min, beta_max = window
        if beta_min < 0 or beta_max > 15:
            print("    WARNING: beta-window outside typical range [0, 15]")

        if beta_min >= beta_max:
            print("    Beta-window inverted (min >= max)")
            return 1

    print("All beta-windows valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
