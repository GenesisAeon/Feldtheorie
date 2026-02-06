"""AeonShell BNF grammar, recursive descent parser, and generator (M1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

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

VALID_STATE_TERMS = frozenset({"ψ", "Ψ", "Φ", "OIPK", "UTAC", "τ*"})
VALID_SYMBOLS = frozenset({"β", "Θ", "ζ", "τ*", "κ"})


@dataclass(frozen=True)
class AeonStatement:
    state_terms: list[str]
    params: dict[str, float]
    consequence: str


class _Lexer:
    """Tokenizer for AeonShell statements."""

    def __init__(self, text: str) -> None:
        self._text = text.strip()
        self._pos = 0

    @property
    def remaining(self) -> str:
        return self._text[self._pos:]

    def at_end(self) -> bool:
        return self._pos >= len(self._text)

    def _skip_ws(self) -> None:
        while self._pos < len(self._text) and self._text[self._pos] in (" ", "\t"):
            self._pos += 1

    def expect(self, token: str) -> None:
        self._skip_ws()
        if not self._text[self._pos:].startswith(token):
            raise ValueError(
                f"Expected '{token}' at position {self._pos}, "
                f"got '{self._text[self._pos:self._pos+len(token)+5]}...'"
            )
        self._pos += len(token)

    def peek(self, token: str) -> bool:
        self._skip_ws()
        return self._text[self._pos:].startswith(token)

    def read_until(self, stop: str) -> str:
        self._skip_ws()
        start = self._pos
        idx = self._text.find(stop, self._pos)
        if idx == -1:
            raise ValueError(f"Expected '{stop}' but not found after position {self._pos}")
        result = self._text[start:idx].strip()
        self._pos = idx
        return result

    def read_number(self) -> float:
        self._skip_ws()
        start = self._pos
        if self._pos < len(self._text) and self._text[self._pos] == "-":
            self._pos += 1
        while self._pos < len(self._text) and self._text[self._pos].isdigit():
            self._pos += 1
        if self._pos < len(self._text) and self._text[self._pos] == ".":
            self._pos += 1
            while self._pos < len(self._text) and self._text[self._pos].isdigit():
                self._pos += 1
        if self._pos == start:
            raise ValueError(f"Expected number at position {self._pos}")
        return float(self._text[start:self._pos])

    def read_consequence(self) -> str:
        self._skip_ws()
        start = self._pos
        while self._pos < len(self._text) and (
            self._text[self._pos].isalnum() or self._text[self._pos] == "-"
        ):
            self._pos += 1
        result = self._text[start:self._pos].strip()
        if not result:
            raise ValueError(f"Expected consequence token at position {start}")
        return result


class AeonShellParser:
    """Recursive descent parser for AeonShell statements.

    Grammar:
        statement   := '⟨' state_terms '⟩' '⊗' '[' params ']' '→' consequence
        state_terms := state_term ('|' state_term)*
        state_term  := 'ψ' | 'Ψ' | 'Φ' | 'OIPK' | 'UTAC' | 'τ*'
        params      := param (',' param)*
        param       := symbol '=' number
        symbol      := 'β' | 'Θ' | 'ζ' | 'τ*' | 'κ'
        consequence := token ('-' token)*
    """

    def parse(self, text: str) -> AeonStatement:
        lexer = _Lexer(text)
        state_terms = self._parse_state_block(lexer)
        lexer.expect("⊗")
        params = self._parse_params_block(lexer)
        lexer.expect("→")
        consequence = lexer.read_consequence()
        return AeonStatement(
            state_terms=state_terms,
            params=params,
            consequence=consequence,
        )

    def _parse_state_block(self, lexer: _Lexer) -> list[str]:
        lexer.expect("⟨")
        raw = lexer.read_until("⟩")
        lexer.expect("⟩")
        terms = [t.strip() for t in raw.split("|") if t.strip()]
        if not terms:
            raise ValueError("AeonShell statement requires at least one state term")
        for term in terms:
            if term not in VALID_STATE_TERMS:
                raise ValueError(
                    f"Invalid state term '{term}'. Valid: {sorted(VALID_STATE_TERMS)}"
                )
        return terms

    def _parse_params_block(self, lexer: _Lexer) -> dict[str, float]:
        lexer.expect("[")
        raw = lexer.read_until("]")
        lexer.expect("]")
        params: dict[str, float] = {}
        for chunk in raw.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "=" not in chunk:
                raise ValueError(f"Invalid param (missing '='): '{chunk}'")
            key, value_str = chunk.split("=", 1)
            key = key.strip()
            if key not in VALID_SYMBOLS:
                raise ValueError(
                    f"Invalid param symbol '{key}'. Valid: {sorted(VALID_SYMBOLS)}"
                )
            try:
                params[key] = float(value_str.strip())
            except ValueError:
                raise ValueError(f"Invalid number for param '{key}': '{value_str.strip()}'")
        if not params:
            raise ValueError("AeonShell statement requires at least one parameter")
        return params


class AeonShellGenerator:
    """Generate AeonShell statement strings from parsed AST."""

    def generate(self, statement: AeonStatement) -> str:
        state = "|".join(statement.state_terms)
        params = ", ".join(f"{key}={value:g}" for key, value in statement.params.items())
        return f"⟨{state}⟩ ⊗ [{params}] → {statement.consequence}"


EXAMPLE_CORPUS = [
    "⟨ψ|OIPK|τ*⟩ ⊗ [β=4.8, Θ=0.5, ζ=-0.1] → Type-VI-Risk",
    "⟨Φ|UTAC⟩ ⊗ [β=3.1, Θ=0.4, κ=0.7] → Resonance-Peak",
    "⟨Ψ|ψ⟩ ⊗ [β=1.2, Θ=0.6, τ*=2.0] → Beta-Drift",
]
