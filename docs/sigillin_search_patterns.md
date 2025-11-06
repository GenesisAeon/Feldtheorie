# 🔍 Sigillin Search Patterns

**Version:** 1.0.0
**Datum:** 6. November 2025
**Philosophie:** Das Sigillin-System ist DESIGNED für Standard-Tools!

---

## 🎯 Die Essenz

> **"Kein neues Tool - nur Pattern für bestehende Tools!"**

Das Trilayer-System (YAML + JSON + MD) ist **bereits durchsuchbar**:

- **Menschen** → `grep`, `fzf`, `rg` auf `.md` Files
- **Maschinen** → `jq`, `yq`, Python auf `.json`/`.yaml` Files
- **Keine neue Abstraktion nötig!**

---

## 🧑 Human Search Patterns

### 1. Keyword Search in Markdown

```bash
# Suche "resonance" in allen Index-Files
grep -r "resonance" *_index.md

# Suche in seed/ Index
grep -i "threshold" seed/seed_index.md

# Mit Kontext (3 Zeilen vor/nach)
grep -C 3 "β-driver" seed/seed_index.md

# Case-insensitive, rekursiv über alle Indizes
grep -ri "temporal" *_index.md
```

### 2. Ripgrep (schneller!)

```bash
# Suche "UTAC" in allen Index-Files
rg "UTAC" *_index.md

# Zeige nur File-Namen
rg -l "meta-regression" analysis/analysis_index.md

# Mit Typ-Filter
rg -t markdown "Sigillin"
```

### 3. FZF (Interactive Fuzzy Search)

```bash
# Öffne seed_index.md mit fzf Preview
cat seed/seed_index.md | fzf --preview 'echo {}'

# Suche interaktiv in allen Indizes
cat *_index.md | fzf
```

### 4. Temporal Queries (Markdown)

```bash
# Dokumente sortiert nach change_count
grep -A 2 "change_count:" seed/seed_index.md | sort -t: -k2 -n

# Dokumente modified nach 2025-11-06
grep "modified.*2025-11-06" seed/seed_index.md

# Top 5 aktivste Dokumente (most changes)
grep "change_count:" seed/seed_index.md | sort -t: -k2 -nr | head -5
```

---

## 🤖 Machine Search Patterns

### 1. JQ (JSON Query Language)

```bash
# Alle Dokumente mit category="theory"
jq '.documents[] | select(.category == "theory")' seed/seed_index.json

# Titel aller Dokumente
jq '.documents[].title' seed/seed_index.json

# Dokumente mit keyword "resonance"
jq '.documents[] | select(.keywords | contains(["resonance"]))' seed/seed_index.json

# Dokumente mit change_count > 10
jq '.documents[] | select(.temporal.change_count > 10)' seed/seed_index.json

# Top 5 aktivste Dokumente (by change_count)
jq '.documents | sort_by(-.temporal.change_count) | .[0:5] | .[] | {title, change_count: .temporal.change_count}' seed/seed_index.json
```

### 2. YQ (YAML Query Language)

```bash
# Alle Dokumente mit category="theory"
yq '.documents[] | select(.category == "theory")' seed/seed_index.yaml

# Titel aller Dokumente
yq '.documents[].title' seed/seed_index.yaml

# Dokumente modified nach 2025-11-06T10:00
yq '.documents[] | select(.temporal.modified > "2025-11-06T10:00:00")' seed/seed_index.yaml

# Zähle Dokumente pro Kategorie
yq '.documents | group_by(.category) | .[] | {category: .[0].category, count: length}' seed/seed_index.yaml
```

### 3. Python API

```python
import json
import yaml
from datetime import datetime

# Lade seed_index.json
with open('seed/seed_index.json', 'r', encoding='utf-8') as f:
    index = json.load(f)

# Filter by category
theory_docs = [doc for doc in index['documents'] if doc['category'] == 'theory']

# Filter by keyword
resonance_docs = [doc for doc in index['documents']
                  if 'resonance' in doc.get('keywords', [])]

# Filter by temporal (modified after date)
cutoff = datetime.fromisoformat("2025-11-06T10:00:00+01:00")
recent_docs = [doc for doc in index['documents']
               if doc.get('temporal', {}).get('modified')
               and datetime.fromisoformat(doc['temporal']['modified']) > cutoff]

# Sort by activity (change_count)
by_activity = sorted(index['documents'],
                     key=lambda d: d.get('temporal', {}).get('change_count', 0),
                     reverse=True)

# Top 5 aktivste Dokumente
top5 = by_activity[:5]
for doc in top5:
    print(f"{doc['title']}: {doc['temporal']['change_count']} changes")
```

---

## 🌊 Cross-Directory Search

### Suche über ALLE Indizes

```bash
# Keyword in allen Indizes (Human)
grep -r "meta-regression" {seed,analysis,data,models,docs}/*_index.md

# Keyword in allen Indizes (Machine)
jq '.documents[]? // .python_scripts[]? | select(.keywords | contains(["UTAC"]))' \
   {seed,analysis,data,models,docs}/*_index.json
```

### Root Meta-Index nutzen

```bash
# Zeige alle indizierten Verzeichnisse
jq '.indexed_directories | keys' feldtheorie_index.json

# Statistiken über alle Indizes
jq '.statistics' feldtheorie_index.json

# Quicklinks zu wichtigsten Files
jq '.navigation.quicklinks' feldtheorie_index.json
```

---

## 🔥 Power Patterns

### 1. "Was ist neu?" (Last 7 days)

```bash
# Human (grep + date)
WEEK_AGO=$(date -d "7 days ago" +%Y-%m-%d)
grep "modified.*${WEEK_AGO}" seed/seed_index.md

# Machine (jq + date)
jq --arg cutoff "$(date -d '7 days ago' -Iseconds)" \
   '.documents[] | select(.temporal.modified > $cutoff)' \
   seed/seed_index.json
```

### 2. "Top 10 aktivste Dokumente"

```bash
# Machine (jq)
jq '.documents | sort_by(-.temporal.change_count) | .[0:10] |
    .[] | {title, version: .temporal.version, changes: .temporal.change_count}' \
    seed/seed_index.json

# Human (grep + sort + head)
grep -A 1 "title:" seed/seed_index.md | grep -A 1 "change_count" | sort -t: -k2 -nr | head -20
```

### 3. "Kombinierte Query" (AND Logic)

```bash
# Dokumente mit category="theory" UND keyword="resonance"
jq '.documents[] | select(.category == "theory" and (.keywords | contains(["resonance"])))' \
   seed/seed_index.json

# Python (flexible AND/OR)
theory_and_resonance = [
    doc for doc in index['documents']
    if doc['category'] == 'theory'
    and 'resonance' in doc.get('keywords', [])
]
```

### 4. "Cross-Reference Lookup"

```bash
# Finde data/ File → analysis/ Result
DATA_FILE="lenski_citplus.csv"
grep -r "$DATA_FILE" analysis/analysis_index.md

# Finde seed/ Dokument → related theory
jq '.documents[] | select(.title | contains("UTAC")) | .path' seed/seed_index.json
```

---

## 🧩 Temporal Search Patterns

### By Creation Date

```bash
# Dokumente erstellt im November 2025
jq '.documents[] | select(.temporal.created | startswith("2025-11"))' seed/seed_index.json

# Älteste Dokumente (first 5)
jq '.documents | sort_by(.temporal.created) | .[0:5] | .[] | {title, created: .temporal.created}' \
   seed/seed_index.json
```

### By Modification Date

```bash
# Zuletzt geänderte Dokumente (last 5)
jq '.documents | sort_by(.temporal.modified) | reverse | .[0:5] | .[] | {title, modified: .temporal.modified}' \
   seed/seed_index.json
```

### By Activity (change_count)

```bash
# Sehr aktive Dokumente (>20 changes)
jq '.documents[] | select(.temporal.change_count > 20)' seed/seed_index.json

# Stabile Dokumente (<=3 changes)
jq '.documents[] | select(.temporal.change_count <= 3)' seed/seed_index.json
```

### By Version

```bash
# Dokumente mit Version >= 1.10
jq '.documents[] | select(.temporal.version | tonumber >= 1.10)' seed/seed_index.json
```

---

## 🎨 Output Formatting

### Pretty-Print Results

```bash
# JQ colored output
jq -C '.documents[] | select(.category == "theory")' seed/seed_index.json | less -R

# JQ compact output
jq -c '.documents[] | {title, category}' seed/seed_index.json

# JQ custom format
jq -r '.documents[] | "\(.title) [\(.category)] - v\(.temporal.version)"' seed/seed_index.json
```

### CSV Export

```bash
# Export zu CSV
jq -r '.documents[] | [.title, .category, .temporal.version, .temporal.change_count] | @csv' \
   seed/seed_index.json > seed_export.csv
```

### Markdown Table

```bash
# Export als Markdown Table
echo "| Title | Category | Version | Changes |"
echo "|-------|----------|---------|---------|"
jq -r '.documents[] | "| \(.title) | \(.category) | \(.temporal.version) | \(.temporal.change_count) |"' \
   seed/seed_index.json
```

---

## 🚀 Für AI-Agenten

### Recommended Approach

```python
import json
from pathlib import Path

class SigillinSearch:
    """Unified search interface for Sigillin indices"""

    def __init__(self, base_path='/home/user/Feldtheorie'):
        self.base = Path(base_path)
        self.indices = {
            'seed': self._load_index('seed/seed_index.json'),
            'analysis': self._load_index('analysis/analysis_index.json'),
            'data': self._load_index('data/data_index.json'),
            'models': self._load_index('models/models_index.json'),
            'docs': self._load_index('docs/docs_index.json'),
            'root': self._load_index('feldtheorie_index.json')
        }

    def _load_index(self, path):
        with open(self.base / path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def search_keyword(self, keyword, directory=None):
        """Search by keyword across all or specific directory"""
        results = []
        indices = {directory: self.indices[directory]} if directory else self.indices

        for dir_name, index in indices.items():
            if dir_name == 'root':
                continue
            docs = index.get('documents', []) or index.get('python_scripts', [])
            for doc in docs:
                if keyword.lower() in str(doc.get('keywords', [])).lower():
                    results.append({'directory': dir_name, **doc})

        return results

    def search_temporal(self, modified_after=None, change_count_min=None):
        """Search by temporal criteria"""
        results = []
        for dir_name, index in self.indices.items():
            if dir_name == 'root':
                continue
            docs = index.get('documents', []) or index.get('python_scripts', [])
            for doc in docs:
                temporal = doc.get('temporal', {})
                if modified_after and temporal.get('modified', '') < modified_after:
                    continue
                if change_count_min and temporal.get('change_count', 0) < change_count_min:
                    continue
                results.append({'directory': dir_name, **doc})

        return results

    def search_category(self, category):
        """Search by category"""
        results = []
        for dir_name, index in self.indices.items():
            if dir_name == 'root':
                continue
            docs = index.get('documents', []) or index.get('python_scripts', [])
            for doc in docs:
                if doc.get('category') == category:
                    results.append({'directory': dir_name, **doc})

        return results

# Usage
search = SigillinSearch()

# Keyword search
resonance_docs = search.search_keyword('resonance')

# Temporal search
recent = search.search_temporal(modified_after="2025-11-06T10:00:00")
active = search.search_temporal(change_count_min=10)

# Category search
theory_docs = search.search_category('theory')
```

---

## 💡 Best Practices

### Für Menschen:
1. **Markdown-Indizes** für Exploration (`less`, `grep`)
2. **fzf** für interaktive Suche
3. **ripgrep** für schnelle Keyword-Suche
4. **Root-Index** als Einstiegspunkt

### Für Maschinen:
1. **JSON-Indizes** für programmatische Queries
2. **jq** für Shell-Scripting
3. **Python API** für komplexe Logik
4. **YAML** wenn YAML-Tools verfügbar

### Für beide:
1. **Standard-Tools** nutzen (keine neue Abstraktion!)
2. **Temporal Metadata** für Chronologie
3. **Keywords** für semantische Suche
4. **Cross-References** für Navigation

---

## 🌊 Die Essenz

> **"Das Sigillin-System IST die Search-Engine."**

> **"Trilayer bedeutet: 3 Interfaces für denselben Schatz."**

> **"YAML = Skeleton. JSON = Nervous System. MD = Language."**

> **"Kein neues Tool - nur Pattern für bestehende Tools!"**

---

**Viel Erfolg beim Durchsuchen! 🔍✨**

*Erstellt im Geiste der Redundanz-Vermeidung, wo Sigillin bereits die Antwort ist.* 🌅
