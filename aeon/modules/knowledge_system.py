"""M3 prototype: knowledge store with ontology categories and TF-IDF scoring."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class KnowledgeEntry:
    entry_id: str
    content: str
    category: str = "general"


class KnowledgeSystem:
    """Knowledge storage, categorization, and retrieval.

    Features:
    - Upsert/delete/get entries with optional category tags
    - TF-IDF-weighted query scoring
    - Category-filtered queries
    - Ontology export (category → entry list)
    """

    def __init__(self) -> None:
        self._entries: dict[str, KnowledgeEntry] = {}

    def upsert(self, entry_id: str, content: str, category: str = "general") -> None:
        self._entries[entry_id] = KnowledgeEntry(
            entry_id=entry_id, content=content, category=category,
        )

    def get(self, entry_id: str) -> KnowledgeEntry | None:
        return self._entries.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False

    def query(
        self,
        text: str,
        limit: int = 5,
        category: str | None = None,
    ) -> list[dict[str, object]]:
        terms = self._tokenize(text)
        if not terms:
            return []

        candidates = self._entries.values()
        if category is not None:
            candidates = [e for e in candidates if e.category == category]

        # Build document frequency table for TF-IDF
        all_doc_terms = [self._tokenize(e.content) for e in candidates]
        n_docs = len(all_doc_terms)
        if n_docs == 0:
            return []

        doc_freq: dict[str, int] = defaultdict(int)
        for doc_terms in all_doc_terms:
            for unique_term in set(doc_terms):
                doc_freq[unique_term] += 1

        scored: list[tuple[float, KnowledgeEntry]] = []
        for entry, doc_terms in zip(candidates, all_doc_terms):
            score = self._tfidf_score(terms, doc_terms, doc_freq, n_docs)
            if score > 0.0:
                scored.append((score, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {"entry_id": entry.entry_id, "content": entry.content, "score": score}
            for score, entry in scored[:limit]
        ]

    def size(self) -> int:
        return len(self._entries)

    def get_categories(self) -> list[str]:
        return sorted({e.category for e in self._entries.values()})

    def export_ontology(self) -> dict[str, list[str]]:
        ontology: dict[str, list[str]] = defaultdict(list)
        for entry in self._entries.values():
            ontology[entry.category].append(entry.entry_id)
        return dict(ontology)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token for token in re.split(r"\W+", text.lower()) if token]

    @staticmethod
    def _tfidf_score(
        query_terms: list[str],
        doc_terms: list[str],
        doc_freq: dict[str, int],
        n_docs: int,
    ) -> float:
        if not query_terms or not doc_terms:
            return 0.0

        doc_term_counts: dict[str, int] = defaultdict(int)
        for t in doc_terms:
            doc_term_counts[t] += 1

        score = 0.0
        for qt in set(query_terms):
            tf = doc_term_counts.get(qt, 0)
            if tf == 0:
                continue
            df = doc_freq.get(qt, 1)
            idf = math.log((n_docs + 1) / (df + 1)) + 1.0
            score += (1 + math.log(tf)) * idf

        return score
