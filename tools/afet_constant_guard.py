from __future__ import annotations

from pathlib import Path

BANNED = ["13.5e6", "37.6", "0.0625", "1.352", "1352.0", "1352.07"]
SCOPES = [Path("aeon"), Path("integration"), Path("src/uatc_core")]


def main() -> int:
    violations: list[str] = []
    for scope in SCOPES:
        if not scope.exists():
            continue
        for py in scope.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            if "AFETConstants" not in text and any(token in text for token in BANNED):
                violations.append(str(py))

    if violations:
        print("AFET constant guard failed. Modules must import AFETConstants:")
        for v in violations:
            print(f" - {v}")
        return 1

    print("AFET constant guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
