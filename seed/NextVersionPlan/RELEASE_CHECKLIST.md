# RELEASE CHECKLIST – UTAC Feldtheorie

> **Version:** ____ (z. B. v2.0.0)  
> **Datum:** ____  
> **Git Tag:** ____  
> **Commit (short SHA):** ____

Diese Checkliste bündelt alle Schritte für ein sauberes, reproduzierbares Release (Code, Daten, Doku, Zitation, DOI).

---

## 0) Vorbedingungen (Quality Gates)

- [ ] **Tests grün:** `pytest -v --tb=short -k "not slow"` → 0 FAIL, **Warnungen < 20**  
- [ ] **Validation vollständig:** 6/6 Konfigurationen, **Seeds ≥ 10**, Aggregation erzeugt (`analysis/results/*`)  
- [ ] **RG‑Evidence:** Data‑Collapse erfolgreich (Visuell + Loss dokumentiert), β vs. log(J/T) monotone Beziehung
- [ ] **Repro ok:** `make reproduce` & **Docker**‑Run erzeugen identische Artefakte
- [ ] **Lizenzen & Attributionen** geprüft (inkl. OCF‑Hinweis)
- [ ] **Changelog gepflegt** (Einträge final, „Unreleased“ → neue Version)

---

## 1) Build & Tests

```bash
# Lokal
python -m pytest -v --tb=short -k "not slow and not api and not tooltip"

# Reproduzierbare Daten + Plots
make reproduce
# oder Docker
docker build -t utac-validate .
docker run --rm -it -v $PWD:/app utac-validate

# CI prüfen (Seeds‑Matrix, Artefakte, Badge)
# https://github.com/GenesisAeon/Feldtheorie/actions/workflows/validation.yml
```

**Akzeptanzkriterien (empfohlen):**
- 0 Test‑Fehler, Warnungen < 20  
- Aggregation vorhanden: `rg_phase2_microscopic_validation.csv/json/_agg.json`  
- Plots vorhanden: `analysis/results/plots/*.png` (β‑Hist, β vs. log(J/T), by‑lattice)

---

## 2) Versionierung & Metadaten

- [ ] **SemVer Bump:** `__version__` / `VERSION` anpassen (z. B. v2.0.0)  
- [ ] **CITATION.cff**: `version` + `date-released` aktualisieren  
- [ ] **README**: Badge‑Links & „How to cite“ aktuell  
- [ ] **METHODS.md**: Datum & ggf. Param‑Tabellen aktualisieren  
- [ ] **zenodo.json**: Felder befüllen (Titel, Creator ORCID/Affil., Keywords)

---

## 3) Artefakte paketieren

```bash
mkdir -p dist
tar -czf dist/utac_phase2_results_plots.tgz analysis/results
cp -v /pfad/zu/Figure_1*.png dist/ || true
```

- [ ] Ergebnisse/Plots komprimiert in `dist/`
- [ ] Datenvolumen ok (keine unnötigen großen Rohdaten)

---

## 4) Rechtliches & Governance

- [ ] **Lizenztexte** vorhanden (MIT/Apache/etc.), Kopfzeilen in Dateien geprüft  
- [ ] **ACKNOWLEDGEMENTS.md** aktuell (OCF‑Attribution, Datenquellen)  
- [ ] **Ethik/Datenschutz**: Keine PII, keine heiklen Daten

---

## 5) Release‑Erstellung

1. **Taggen & signieren (optional):**
   ```bash
   git tag -s vX.Y.Z -m "UTAC Feldtheorie vX.Y.Z"
   git push origin vX.Y.Z
   ```
2. **GitHub Release** anlegen:
   - Titel: `UTAC Feldtheorie vX.Y.Z`
   - Text: Highlights + Auszug aus `CHANGELOG.md`
   - Anhänge: `dist/utac_phase2_results_plots.tgz`, Abbildungen (Figure 1a/b)
3. **Zenodo DOI**:
   - GitHub‑Zenodo‑Integration prüfen (autom. DOI) *oder* manuelles Upload‑Record
   - DOI im **README**‑Badge & **CITATION.cff** eintragen

---

## 6) Post‑Release

- [ ] **README** final mit DOI‑Badge
- [ ] **CHANGELOG „Unreleased“** neu öffnen (nächste Version: vX.Y.(Z+1)‑dev)
- [ ] **Paper/Preprint** aktualisieren (METHODS, Figure 1, Caption)
- [ ] **Ankündigung** (Communities/Foren), **Issue‑Board** mit Next‑Milestones
- [ ] **Container/Image** ins Registry (GHCR) pushen (optional)

---

## 7) Rollback‑Plan (Falls nötig)

- [ ] Vorherigen Release‑Tag dokumentiert (vPrev)  
- [ ] `git revert`/`git tag -d` Verfahren geklärt  
- [ ] README/DOI‑Hinweise zurückrollen (Notiz in Release Notes)

---

**Abzeichnung:**  
- Owner: ________  Datum: ________  
- Review: ________ Datum: ________
