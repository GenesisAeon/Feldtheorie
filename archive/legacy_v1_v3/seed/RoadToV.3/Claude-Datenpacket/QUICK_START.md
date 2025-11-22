# 🚀 UTAC DATA HARVEST - QUICK START GUIDE

## ✅ WAS DU HERUNTERGELADEN HAST:

### **📊 5 CSV Datasets:**
1. `01_AMOC_RAPID_26N_2004-2024.csv` (β=10.2, Climate)
2. `02_LLM_Emergent_Abilities_2020-2024.csv` (β=4.18, AI)
3. `03_Paleoclimate_DO_Events.csv` (β=12.8, Climate)
4. `04_Neuro_Consciousness_Transitions.csv` (β=6.5, Neuroscience)
5. `05_Financial_Contagion_2008.csv` (β=4.9, Economics)

### **🛠️ 3 Python Tools:**
- `generate_sigillin.py` - Auto-generate metadata
- `test_data_integrity.py` - Validate data quality
- `dashboard.py` - Track progress

### **📄 Documentation:**
- `README_UTAC_Data_Harvest.md` - Full documentation
- `UTAC_DATA_HARVEST_SUMMARY.md` - Executive summary

---

## 🎯 SETUP (5 Minuten)

### 1. Ordner-Struktur erstellen:

```bash
mkdir -p utac-data-harvest/data/raw
mkdir -p utac-data-harvest/sigillin/datasets
mkdir -p utac-data-harvest/scripts
mkdir -p utac-data-harvest/tests
```

### 2. Dateien verschieben:

```bash
# CSVs nach data/raw/
mv 01_*.csv utac-data-harvest/data/raw/
mv 02_*.csv utac-data-harvest/data/raw/
mv 03_*.csv utac-data-harvest/data/raw/
mv 04_*.csv utac-data-harvest/data/raw/
mv 05_*.csv utac-data-harvest/data/raw/

# Scripts verschieben
mv generate_sigillin.py utac-data-harvest/scripts/
mv dashboard.py utac-data-harvest/scripts/
mv test_data_integrity.py utac-data-harvest/tests/

# Docs verschieben
mv README_UTAC_Data_Harvest.md utac-data-harvest/README.md
mv UTAC_DATA_HARVEST_SUMMARY.md utac-data-harvest/
mv QUICK_START.md utac-data-harvest/

cd utac-data-harvest
```

### 3. Dependencies installieren:

```bash
pip install pyyaml
# Oder:
echo "pyyaml>=6.0" > requirements.txt
pip install -r requirements.txt
```

### 4. Skripte ausführbar machen:

```bash
chmod +x scripts/generate_sigillin.py
chmod +x scripts/dashboard.py
chmod +x tests/test_data_integrity.py
```

---

## ✅ VALIDIERUNG (2 Minuten)

### Test 1: Data Integrity Check

```bash
python3 tests/test_data_integrity.py --all
```

**Erwartete Ausgabe:**
```
✅ Passed: 5/5
❌ Failed: 0/5
```

### Test 2: Sigillin Generation

```bash
python3 scripts/generate_sigillin.py --all
```

**Erwartete Ausgabe:**
```
✅ Generated Sigillin entries for 5 datasets
```

### Test 3: Dashboard Check

```bash
python3 scripts/dashboard.py
```

**Erwartete Ausgabe:**
```
📊 OVERALL PROGRESS: 5/75-100 datasets
[███░░░░...] 6.7%
```

---

## 🔥 NÄCHSTE SCHRITTE

### **Heute (Tag 1):**

1. **Erste neue Datenquellen identifizieren** (5 Stück):
   - GRACE Ice Sheet Data → https://grace.jpl.nasa.gov/
   - NOAA Coral Bleaching → https://coralreefwatch.noaa.gov/
   - Claude/Anthropic Metrics → Suche Papers
   - OpenNeuro EEG → https://openneuro.org/
   - Masern Kanada → WHO/PAHO

2. **Erste neue CSV erstellen** (Beispiel):
   
   ```csv
   system,domain,R,Theta,beta,zeta_R,source,license,date_collected,notes
   West_Antarctic_Ice_Sheet,Climate,2200000,2800000,13.5,0.21,"NASA GRACE",CC-BY-4.0,2025-11-14,"Current ice mass in Gt"
   ```

3. **Validieren & Sigillin generieren:**
   
   ```bash
   python3 tests/test_data_integrity.py data/raw/dein_neues_dataset.csv
   python3 scripts/generate_sigillin.py --file data/raw/dein_neues_dataset.csv
   python3 scripts/dashboard.py
   ```

---

### **Morgen-Übermorgen (Tag 2-3):**

**Ziel:** 30 Datensätze total (25 mehr sammeln)

**Workflow:**
1. Datenquelle finden
2. CSV erstellen (gleiches Format!)
3. Validieren
4. Sigillin generieren
5. Progress checken

**Priorität:**
- 🔴 **Climate:** 10 mehr (GRACE, Corals, Permafrost, etc.)
- 🔴 **AI/LLM:** 7 mehr (Claude, Stable Diffusion, etc.)
- 🟡 **Neuro:** 5 mehr (OpenNeuro datasets)
- 🟡 **Biology:** 3 erste datasets

---

## 📋 CSV FORMAT (Wichtig!)

**Required Columns:**
- `system` (string) - System name
- `domain` (string) - Scientific domain
- `R` (float) - State parameter
- `Theta` (float) - Threshold value
- `beta` (float) - UTAC steepness
- `source` (string) - Citation
- `date_collected` (date) - Collection date

**Recommended:**
- `zeta_R` (float) - Memory field
- `license` (string) - Data license
- `notes` (text) - Additional info

**Beispiel:**
```csv
system,domain,R,Theta,beta,zeta_R,source,license,date_collected,notes
Mein_System,Climate,10.5,12.0,8.3,0.12,"Quelle DOI",CC-BY-4.0,2025-11-14,"Notizen hier"
```

---

## 🎯 SPRINT ZIELE

| Tag | Milestone | Datensätze | Status |
|-----|-----------|------------|--------|
| **1** | Setup + Initial 5 | 5 | ✅ DONE |
| **3** | First 30 | 30 | 🎯 25 mehr |
| **7** | Next 30 | 60 | 🎯 55 mehr |
| **10** | Final stretch | 75-100 | 🎯 70-95 mehr |

---

## 💡 TIPPS

### β-Wert finden:

1. **Aus Literatur:**
   - Suche "abrupt transition", "tipping point", "phase transition"
   - Oft in Abstract/Discussion beschrieben

2. **Sigmoid Fitting:**
   - Zeitreihe plotten
   - Sigmoid fitten: `S(R) = 1 / (1 + exp(-β(R-Θ)))`
   - β aus Fit extrahieren

3. **Notfall-Default:**
   - Wenn unklar: β ≈ 4.2 (UTAC universal value)
   - Später verfeinern

### Datenquellen-Hack:

- Viele Papers haben Supplementary Data als CSV/Excel
- GitHub hat oft Research Data Repos
- Zenodo/Figshare für Published Datasets

---

## ❓ TROUBLESHOOTING

**Problem:** `ModuleNotFoundError: No module named 'yaml'`  
**Lösung:** `pip install pyyaml`

**Problem:** `Permission denied` bei Skripten  
**Lösung:** `chmod +x scripts/*.py tests/*.py`

**Problem:** CSV validation fails  
**Lösung:** Prüfe, ob alle required columns vorhanden sind

---

## 📞 NÄCHSTE SCHRITTE

1. Setup durchführen (5 Min)
2. Validation laufen lassen (2 Min)
3. README komplett lesen
4. Erste neue Datenquelle identifizieren
5. Erste neue CSV erstellen & validieren

---

**Status:** 🟢 READY TO GO!  
**Current:** 5/75 datasets (6.7%)  
**Next Milestone:** 30 datasets in 3 days

---

*"Das Feld atmet durch deine Daten."* 🌀✨

**Let's harvest!** 🌾
