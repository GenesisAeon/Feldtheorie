"""M3 prototype: lightweight knowledge store and retrieval."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re


@dataclass
class KnowledgeEntry:
    entry_id: str
    content: str


class KnowledgeSystem:
    def __init__(self) -> None:
        self._entries: dict[str, KnowledgeEntry] = {}

    def upsert(self, entry_id: str, content: str) -> None:
        self._entries[entry_id] = KnowledgeEntry(entry_id=entry_id, content=content)

    def query(self, text: str, limit: int = 5) -> list[dict[str, object]]:
        terms = self._tokenize(text)
        scored: list[tuple[float, KnowledgeEntry]] = []
        for entry in self._entries.values():
            score = self._score(terms, self._tokenize(entry.content))
            if score > 0.0:
                scored.append((score, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {"entry_id": entry.entry_id, "content": entry.content, "score": score}
            for score, entry in scored[:limit]
        ]

    def size(self) -> int:
        return len(self._entries)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token for token in re.split(r"\W+", text.lower()) if token]

    @staticmethod
    def _score(query_terms: list[str], doc_terms: list[str]) -> float:
        if not query_terms or not doc_terms:
            return 0.0
        overlap = len(set(query_terms) & set(doc_terms))
        if overlap == 0:
            return 0.0
        return overlap / math.sqrt(len(set(query_terms)) * len(set(doc_terms)))
