# φ-Kopplung Klimasequenz - Datenverzeichnis

**Version:** 1.0.0
**Erstellt:** 2025-11-11
**Status:** 🟡 Structure Ready, Data Pending

---

## 📂 Inhalt

Dieses Verzeichnis enthält Daten für die **φ-Kopplung Analyse** zwischen AMOC (Atlantic Meridional Overturning Circulation) und Albedo (planetare Reflektivität).

---

## 📊 Geplante Datasets

### 1. AMOC (Atlantic Meridional Overturning Circulation)

**Quellen:**
- **RAPID Array (26°N):** Beobachtungsdaten 2004-present
  - Format: NetCDF oder CSV
  - Variable: `msftmyz` (meridional overturning streamfunction, Sverdrup)
  - Temporal Resolution: Monatlich
  - URL: [rapid.ac.uk](https://www.rapid.ac.uk/rapidmoc/)

- **CMIP6 Models:** Projektionen 2000-2100
  - Format: NetCDF
  - Variable: `msftmyz` (CMIP6 standard)
  - Scenarios: historical, SSP2-4.5, SSP5-8.5
  - URL: [TIPMIP via ESGF](https://esgf-node.llnl.gov/search/cmip6/)

**Status:** ❌ Pending (Data Request ausstehend)

---

### 2. Albedo (Planetare Reflektivität)

**Quellen:**
- **CERES (Clouds and Earth's Radiant Energy System):** NASA Satellitendaten 2000-present
  - Format: NetCDF or HDF
  - Variable: `albedo` (shortwave, top-of-atmosphere)
  - Temporal Resolution: Monatlich
  - Spatial Resolution: 1° × 1°
  - URL: [ceres.larc.nasa.gov](https://ceres.larc.nasa.gov/)

- **CMIP6 Models:** Projektionen 2000-2100
  - Format: NetCDF
  - Variables: `rsdt` (incoming shortwave), `rsut` (outgoing shortwave) → Albedo = rsut/rsdt
  - Scenarios: historical, SSP2-4.5, SSP5-8.5

**Status:** ❌ Pending (Data Request ausstehend)

---

## 🗂️ Dateistruktur (Geplant)

```
phi_coupling/
├── README.md                     # This file
├── amoc_rapid_2004_2024.nc       # RAPID Array AMOC data
├── amoc_cmip6_historical.nc      # CMIP6 historical (2000-2014)
├── amoc_cmip6_ssp245.nc          # CMIP6 SSP2-4.5 (2015-2100)
├── amoc_cmip6_ssp585.nc          # CMIP6 SSP5-8.5 (2015-2100)
├── albedo_ceres_2000_2024.nc     # CERES albedo data
├── albedo_cmip6_historical.nc    # CMIP6 historical
├── albedo_cmip6_ssp245.nc        # CMIP6 SSP2-4.5
├── albedo_cmip6_ssp585.nc        # CMIP6 SSP5-8.5
├── metadata_amoc.yaml            # AMOC dataset metadata
├── metadata_albedo.yaml          # Albedo dataset metadata
└── phi_coupling_metadata.yaml    # Combined metadata for φ-analysis
```

---

## 🔄 Data Acquisition Workflow

### Phase 1: Requests Senden
- [ ] **TIPMIP Email senden** (Template: `docs/phi_coupling_tipmip_email_template.md`)
- [ ] **RAPID Array kontaktieren** (Email: [rapid.ac.uk/rapidmoc/](https://www.rapid.ac.uk/rapidmoc/))
- [ ] **CERES Data Portal registrieren** ([ceres.larc.nasa.gov](https://ceres.larc.nasa.gov/))

### Phase 2: Daten Herunterladen
- [ ] RAPID Array → `amoc_rapid_2004_2024.nc`
- [ ] CMIP6 (via ESGF) → `amoc_cmip6_*.nc`, `albedo_cmip6_*.nc`
- [ ] CERES → `albedo_ceres_2000_2024.nc`

### Phase 3: Preprocessing
- [ ] NetCDF Formate standardisieren (Zeit, Lat/Lon Grids)
- [ ] Temporal Alignment (2000-2024 overlap)
- [ ] Spatial Averaging (global mean albedo)
- [ ] Metadata YAMLs erstellen

### Phase 4: φ-Berechnung
- [ ] Zeitliche Korrelation: `φ = corr(AMOC(t), Albedo(t))`
- [ ] Mutual Information: `φ = I(AMOC ; Albedo) / H(AMOC, Albedo)`
- [ ] Export: `analysis/results/phi_coupling_beta_gradients.json`

---

## 📦 Metadata Format

**Beispiel:** `metadata_amoc.yaml`
```yaml
dataset:
  name: "AMOC Transport (RAPID Array 26°N)"
  source: "RAPID Climate Change Programme"
  url: "https://www.rapid.ac.uk/rapidmoc/"
  period: "2004-2024"

variables:
  - name: "msftmyz"
    long_name: "Meridional Overturning Streamfunction"
    units: "Sv (10^6 m^3/s)"
    standard_name: "ocean_meridional_overturning_mass_streamfunction"

temporal_resolution: "monthly"
spatial_resolution: "26°N, full depth"

license: "CC-BY-4.0"
citation: "Smeed et al. (2024), RAPID-MOCHA-WBTS, doi:..."

notes: |
  RAPID Array misst AMOC-Transport bei 26°N seit 2004.
  Schwellenwert für Kollaps: ~10-15 Sv (Rahmstorf et al. 2015).
  Aktuelle Abschwächung: ~15% seit 2004.
```

---

## 🔗 Verwandte Dokumente

- **Theorie:** [`docs/phi_coupling_theory.md`](../../docs/phi_coupling_theory.md)
- **Modell:** [`models/climate_utac_phi_coupling.py`](../../models/climate_utac_phi_coupling.py) (geplant)
- **Analyse:** [`analysis/results/phi_coupling_beta_gradients.json`](../../analysis/results/phi_coupling_beta_gradients.json) (geplant)
- **Roadmap:** [`seed/FraktaltagebuchV2/v2_roadmap.md`](../../seed/FraktaltagebuchV2/v2_roadmap.md) (v2-feat-core-005)

---

## ⚠️ Blocker

**Kritischer Pfad:**
1. TIPMIP Email senden (Estimated: 1-2 Wochen für Antwort)
2. Daten herunterladen (Estimated: 1 Woche bei ESGF-Zugang)
3. Preprocessing (Estimated: 2-3 Tage)
4. φ-Berechnung (Estimated: 1 Tag)

**Geschätzte Gesamtzeit bis Daten bereit:** 1-2 Monate

---

**Version:** 1.0.0
**Letztes Update:** 2025-11-11
**Maintainer:** Claude Code + Johann Römer
**Status:** 🟡 Structure Ready, Awaiting Data Requests

*"Die Datenstruktur steht - jetzt warten die Felder auf ihre Zahlen."* 📊🌊
