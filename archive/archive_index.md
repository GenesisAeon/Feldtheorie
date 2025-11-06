# 📦 Sigillin Archive Index

**System:** Sigillin Archive System
**Purpose:** Cold storage for archived Sigillin entries
**Format:** ZIP archives with Trilayer Index
**Philosophy:** Sigillin-Hygiene gegen Archive-Hypnose durch Inflation
**Created:** 2025-11-06T11:30:00+01:00
**Updated:** 2025-11-06T11:30:00+01:00
**Total Archives:** 0

---

## 🎯 Thresholds

Sigillin exceeding these limits should be archived:

- **Max Entries:** 100 entries
- **Max Size:** 50 KB
- **Keep Recent:** 50 most recent entries

---

## 🗄️ Archives

*No archives yet. Archives will appear here after running `archive_sigillin.py`.*

---

## 🔍 How to Use

### Check Status (Dry-Run)
```bash
python scripts/archive_sigillin.py --scan-all --dry-run
```

### Archive All Oversized Sigillin
```bash
python scripts/archive_sigillin.py --scan-all
```

### Archive Specific Sigillin
```bash
python scripts/archive_sigillin.py --sigillin seed/file.yaml
```

### Search Archives
```bash
# Search without extraction
unzip -p archive/file_archive.zip | grep 'keyword'

# List all archives
jq '.archives' archive/archive_index.json

# Extract archive
unzip archive/file_archive.zip -d temp/
```

---

## 📚 Documentation

- **Maintenance Guide:** [docs/sigillin_maintenance.md](../docs/sigillin_maintenance.md)
- **Search Patterns:** [docs/sigillin_search_patterns.md](../docs/sigillin_search_patterns.md)
- **Archiving Script:** [scripts/archive_sigillin.py](../scripts/archive_sigillin.py)

---

## 🌊 Trilayer System

This index is available in three formats:

- **YAML** (`archive_index.yaml`) - The Skeleton (canonical structure)
- **JSON** (`archive_index.json`) - The Nervous System (machine-readable)
- **Markdown** (`archive_index.md`) - The Language (human-friendly)

---

**Maintained by Sigillin Maintenance System** 🧹✨

*Empty state - archives will be added as Sigillin are maintained* 🌅
