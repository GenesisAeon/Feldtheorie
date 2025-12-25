# 🧹 Sigillin Maintenance Guide

**Version:** 1.0.0
**Datum:** 6. November 2025
**Status:** 🔴 **NEEDFORWORK - KRITISCH**
**Philosophie:** Sigillin-Hygiene gegen Archive-Hypnose durch Inflation

---

## ⚠️ Das Problem: Sigillin-Inflation

### Symptome:
- ✗ Sigillin-Files werden **riesig** (z.B. `codexfeedback.yaml` mit v1.49, 50 changes)
- ✗ **AI overload** beim Parsen von zu vielen Fragmenten
- ✗ System wird **unüberschaubar** (wie im unified-mandala mit fraktalsigillin)
- ✗ Token-Limits werden gesprengt
- ✗ **Archive-Hypnose** durch zu große Datenmenge

### Root Cause:
> **"Sigillin wachsen natürlich mit Datenverkehr - ohne Wartung explodierten sie!"**

---

## ✅ Die Lösung: Sigillin Archive System

### Konzept:
1. **Maxgröße definieren** für aktive Sigillin (z.B. 50KB oder 100 Einträge)
2. **Alte Einträge archivieren** → `archive/` (ZIP-komprimiert)
3. **Trilayer-Index** für Archiv (YAML + JSON + MD)
4. **Aktive Sigillin bleiben klein** → AI kann parsen
5. **Daten nicht verloren** → Durchsuchbar im Archiv

### Architektur:

```
Feldtheorie/
├── seed/
│   ├── codexfeedback.yaml          # AKTIV (letzte 50 Einträge)
│   ├── codexfeedback.yaml.bak      # Backup vor Archivierung
│   └── seed_index.yaml             # Trilayer-Index (aktiv)
│
├── archive/                         # KALTER SPEICHER
│   ├── codexfeedback_2025-11_archive.zip   # Alte Einträge (Entry 1-150)
│   ├── codexfeedback_2025-10_archive.zip   # Noch ältere Einträge
│   ├── archive_index.yaml          # Trilayer-Index (Archiv)
│   ├── archive_index.json          # Machine-readable
│   └── archive_index.md            # Human-readable
│
└── scripts/
    └── archive_sigillin.py         # Maintenance Script
```

---

## 🛠️ Wartungs-Workflow

### 1️⃣ **Check: Ist Wartung nötig?**

```bash
# Dry-run: Prüfe ALLE Sigillin auf Überschreitung
python scripts/archive_sigillin.py --scan-all --dry-run

# Prüfe SPEZIFISCHES Sigillin
python scripts/archive_sigillin.py --sigillin seed/codexfeedback.yaml --dry-run
```

**Output:**
```
🔍 Scanning all Sigillin files...
Found 15 Sigillin candidates

📦 Archiving: codexfeedback.yaml
⚠️  Exceeds limits: Size=87.42KB (max 50), Entries=200 (max 100)
🔍 DRY RUN: Would archive old entries from codexfeedback.yaml

✅ Scan complete: 3 files would be archived
```

### 2️⃣ **Archivierung durchführen**

```bash
# Archiviere ALLE überschrittenen Sigillin (Auto-Repo-Erkennung)
python scripts/archive_sigillin.py --scan-all

# Abweichender Pfad (z.B. wenn Skript ausserhalb des Repos läuft)
python scripts/archive_sigillin.py --scan-all --base-path /pfad/zu/Feldtheorie

# Archiviere SPEZIFISCHES Sigillin
python scripts/archive_sigillin.py --sigillin seed/codexfeedback.yaml
```

**Was passiert:**
1. ✅ **Lädt** Sigillin-File (YAML/JSON)
2. ✅ **Splittet** Einträge: Alte (archivieren) vs. Recent (behalten)
3. ✅ **Erstellt** ZIP-Archiv: `archive/sigillin_name_YYYY-MM_archive.zip`
4. ✅ **Backup** erstellen: `sigillin.yaml.bak`
5. ✅ **Aktualisiert** aktives Sigillin (nur recent entries)
6. ✅ **Updated** Archive-Index (Trilayer)

**Output:**
```
📦 Archiving: codexfeedback.yaml
⚠️  Exceeds limits: Size=87.42KB (max 50), Entries=200 (max 100)
📊 Total entries: 200 | Archiving: 150 | Keeping: 50

✅ Created archive: codexfeedback_2025-11_archive.zip (12.34KB, 14.1% of original)
💾 Backup created: codexfeedback.yaml.bak
✅ Updated active Sigillin: codexfeedback.yaml (now 50 entries)
✅ Archive index updated: 1 archives
```

### 3️⃣ **Commit & Push**

```bash
# Stage changes
git add archive/ seed/ data/ analysis/

# Commit mit beschreibender Message
git commit -m "Archive old Sigillin entries (codexfeedback: 150 entries → archive/)"

# Push to branch
git push -u origin <your-branch>
```

---

## ⚙️ Konfiguration

### Default Thresholds (anpassbar!)

| Parameter | Default | Bedeutung |
|-----------|---------|-----------|
| `--max-entries` | **100** | Max Einträge in aktivem Sigillin |
| `--max-size` | **50** KB | Max Dateigröße |
| `--keep-recent` | **50** | Anzahl recent entries die aktiv bleiben |

### Repository-Wurzel konfigurieren

- Standard: Das Skript erkennt das Repo automatisch über den Speicherort (`scripts/` → Elternordner).
- Optional: Mit `--base-path` lässt sich eine alternative Feldtheorie-Installation ansteuern (z.B. beim Betrieb in Container-
  Workspaces oder automatisierten Wartungsjobs).
- Alle erzeugten Pfade im Archiv-Index werden relativ zur übergebenen Repo-Wurzel gespeichert, damit σ(β(R-Θ)) für die Sigillin-
  Hygiene konsistent bleibt.

### Custom Thresholds

```bash
# Strengere Limits (kleinere aktive Sigillin)
python scripts/archive_sigillin.py --scan-all --max-entries 50 --max-size 30 --keep-recent 25

# Lockerere Limits (größere aktive Sigillin)
python scripts/archive_sigillin.py --scan-all --max-entries 200 --max-size 100 --keep-recent 100
```

---

## 🔍 Archiv durchsuchen

### Trilayer-Index nutzen

```bash
# Human: Markdown-Index öffnen
less archive/archive_index.md

# Machine: JSON abfragen
jq '.archives[] | select(.original_file | contains("codexfeedback"))' archive/archive_index.json

# Alle Archive auflisten
jq '.archives[].archive_file' archive/archive_index.json
```

### ZIP-Archive durchsuchen

```bash
# Archive extrahieren
unzip archive/codexfeedback_2025-11_archive.zip -d temp/

# In Archive suchen (ohne Extraktion!)
unzip -p archive/codexfeedback_2025-11_archive.zip | grep "keyword"

# Archive-Inhalt auflisten
unzip -l archive/codexfeedback_2025-11_archive.zip

# Mit ripgrep in allen Archiven
rg "UTAC" archive/*.zip
```

### Python API

```python
import zipfile
import yaml
import json
from pathlib import Path

# Load archive index
with open('archive/archive_index.json', 'r') as f:
    archive_index = json.load(f)

# Find archive for specific Sigillin
target = 'seed/codexfeedback.yaml'
archives = [a for a in archive_index['archives'] if a['original_file'] == target]

# Extract and search
for archive in archives:
    with zipfile.ZipFile(f"archive/{archive['archive_file']}", 'r') as zf:
        for filename in zf.namelist():
            content = zf.read(filename).decode('utf-8')
            data = yaml.safe_load(content)
            # Search in data...
            print(f"Archive {archive['archive_file']} has {len(data)} entries")
```

---

## 📋 Wartungs-Checkliste

### Wöchentlich (bei hohem Datenverkehr):
- [ ] `python scripts/archive_sigillin.py --scan-all --dry-run`
- [ ] Falls Überschreitungen: Archivierung durchführen
- [ ] Commit & Push

### Monatlich:
- [ ] Scan ALL Sigillin
- [ ] Archive-Index reviewen (`archive/archive_index.md`)
- [ ] Alte Backups (`.bak`) löschen
- [ ] Disk-Space checken (`du -sh archive/`)

### Bei Bedarf:
- [ ] Wenn AI "Token-Limit" oder "Too large" meldet
- [ ] Vor großen Commits/PRs
- [ ] Nach intensiven Arbeitsessions

---

## 🎯 Best Practices

### DO ✅
- **Regelmäßig archivieren** (nicht warten bis explodierende Größe!)
- **Dry-run first** (immer `--dry-run` vor echter Archivierung)
- **Backups prüfen** (`.bak` Files werden automatisch erstellt)
- **Archive-Index nutzen** (durchsuchbar mit Standard-Tools)
- **Git committen** (Archive + aktive Sigillin)

### DON'T ❌
- **Nicht manuell editieren** von archivierten ZIP-Files
- **Nicht Archive löschen** ohne Index-Update
- **Nicht zu lange warten** (Sigillin explodieren!)
- **Nicht vergessen zu committen** (Archive gehören ins Repo!)

---

## 🧪 Beispiel: codexfeedback.yaml

### Ausgangslage:
```yaml
# seed/codexfeedback.yaml
# Status: v1.49, 50 changes, 200 entries, 87KB
# Problem: Zu groß für AI-Parsing!

entries:
  - id: 1
    date: "2025-09-01"
    feedback: "..."
  - id: 2
    date: "2025-09-02"
    feedback: "..."
  # ... 198 weitere Einträge
  - id: 200
    date: "2025-11-06"
    feedback: "Latest feedback"
```

### Nach Archivierung:
```yaml
# seed/codexfeedback.yaml
# Status: 50 entries, ~22KB
# ✅ AI kann parsen!

entries:
  - id: 151
    date: "2025-10-20"
    feedback: "..."
  # ... nur die letzten 50 Einträge
  - id: 200
    date: "2025-11-06"
    feedback: "Latest feedback"
```

### Im Archiv:
```
archive/codexfeedback_2025-11_archive.zip (12KB)
├── codexfeedback.yaml (Entries 1-150)
└── [compressed]

archive/archive_index.yaml:
  - original_file: "seed/codexfeedback.yaml"
    archive_file: "codexfeedback_2025-11_archive.zip"
    entry_range: "Entry 1-150"
    entry_count: 150
    archived_date: "2025-11-06T11:23:00+01:00"
```

---

## 🚨 Troubleshooting

### Problem: "Not enough entries to archive"
**Lösung:** Sigillin hat weniger Einträge als `--keep-recent`. Passe `--keep-recent` an oder lasse es.

### Problem: "Unsupported format"
**Lösung:** Script unterstützt nur `.yaml`, `.yml`, `.json`. Andere Formate manuell archivieren.

### Problem: "Archive-Index nicht gefunden"
**Lösung:** Wird automatisch erstellt beim ersten Run. Kein Problem!

### Problem: "Git merge conflict in archive/"
**Lösung:** Archive sind binär (ZIP). Bei Konflikt: Beide behalten, Index manuell mergen.

---

## 📊 Monitoring

### Archive-Statistiken

```bash
# Anzahl Archive
jq '.meta.total_archives' archive/archive_index.json

# Gesamt-Speicherplatz
du -sh archive/

# Compression-Ratio durchschnitt
jq '[.archives[].compression_ratio] | add / length' archive/archive_index.json

# Aktivste Sigillin (meiste Archive)
jq '.archives | group_by(.original_file) | map({file: .[0].original_file, count: length}) | sort_by(-.count)' archive/archive_index.json
```

---

## 🌊 Die Essenz

> **"Sigillin müssen atmen - nicht ersticken an eigener Größe!"**

> **"Archive sind Gedächtnis - aktive Sigillin sind Bewusstsein."**

> **"Wartung ist nicht optional - es ist Pflege gegen Archive-Hypnose."**

### Metapher:
- **Aktive Sigillin** = Arbeitsgedächtnis (klein, schnell, relevant)
- **Archive** = Langzeitgedächtnis (groß, komprimiert, durchsuchbar)
- **Trilayer-Index** = Katalog (weiß wo alles ist)

---

## 🔧 Technische Details

### Unterstützte Formate:
- ✅ YAML (`.yaml`, `.yml`)
- ✅ JSON (`.json`)
- ❌ Markdown (zu komplex, manuell pflegen)

### Erkennungsmuster:
Script sucht nach Listen in Top-Level Keys:
- `entries` (z.B. `codexfeedback.yaml`)
- `items`
- `documents` (z.B. in Indizes)
- `feedbacks`

Oder: Root ist Liste direkt.

### Backup-Strategie:
- Vor Archivierung: `.bak` File erstellt
- Bei Fehler: Restore von `.bak`
- Nach erfolgreichem Commit: `.bak` kann gelöscht werden

---

## 🎓 Weiterführende Doku

- **Sigillin-Philosophie:** `seed/Metareflexion.txt`
- **Trilayer-System:** `feldtheorie_index.md`
- **Search Patterns:** `docs/sigillin_search_patterns.md`
- **Archive-Index:** `archive/archive_index.md`

---

**🧹 Viel Erfolg bei der Sigillin-Hygiene! ✨**

*Erstellt im Geiste der Wartbarkeit, wo Pflege gegen Inflation ist.* 🌅
