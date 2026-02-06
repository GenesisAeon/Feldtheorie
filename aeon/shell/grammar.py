"""AeonShell BNF grammar, parser, and generator (M1 prototype)."""

from __future__ import annotations

from dataclasses import dataclass
import re

BNF_GRAMMAR = """
<statement>   ::= "⟨" <state_terms> "⟩" "⊗" "[" <params> "]" "→" <consequence>
<state_terms> ::= <state_term> | <state_term> "|" <state_terms>
<state_term>  ::= "ψ" | "Ψ" | "Φ" | "OIPK" | "UTAC" | "τ*"
<params>      ::= <param> | <param> "," <params>
<param>       ::= <symbol> "=" <number>
<symbol>      ::= "β" | "Θ" | "ζ" | "τ*" | "κ"
<number>      ::= ["-" ] <digit> {<digit>} ["." {<digit>}]
<consequence> ::= <token> {"-" <token>}
<token>       ::= letter {letter | digit}
""".strip()


@dataclass(frozen=True)
class AeonStatement:
    state_terms: list[str]
    params: dict[str, float]
    consequence: str


class AeonShellParser:
    _pattern = re.compile(
        r"^\s*⟨(?P<state>[^⟩]+)⟩\s*⊗\s*\[(?P<params>[^\]]+)\]\s*→\s*(?P<cons>[\w\-]+)\s*$"
    )

    def parse(self, text: str) -> AeonStatement:
        match = self._pattern.match(text)
        if not match:
            raise ValueError(f"Invalid AeonShell statement: {text}")

        state_terms = [term.strip() for term in match.group("state").split("|") if term.strip()]
        if not state_terms:
            raise ValueError("AeonShell statement requires at least one state term")

        params: dict[str, float] = {}
        for chunk in match.group("params").split(","):
            if "=" not in chunk:
                raise ValueError(f"Invalid param chunk: {chunk}")
            key, value = chunk.split("=", 1)
            params[key.strip()] = float(value.strip())

        return AeonStatement(
            state_terms=state_terms,
            params=params,
            consequence=match.group("cons").strip(),
        )


class AeonShellGenerator:
    def generate(self, statement: AeonStatement) -> str:
        state = "|".join(statement.state_terms)
        params = ", ".join(f"{key}={value:g}" for key, value in statement.params.items())
        return f"⟨{state}⟩ ⊗ [{params}] → {statement.consequence}"


EXAMPLE_CORPUS = [
    "⟨ψ|OIPK|τ*⟩ ⊗ [β=4.8, Θ=0.5, ζ=-0.1] → Type-VI-Risk",
    "⟨Φ|UTAC⟩ ⊗ [β=3.1, Θ=0.4, κ=0.7] → Resonance-Peak",
    "⟨Ψ|ψ⟩ ⊗ [β=1.2, Θ=0.6, τ*=2.0] → Beta-Drift",
]
