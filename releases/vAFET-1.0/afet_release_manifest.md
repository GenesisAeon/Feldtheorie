# AFET v1.0 Release Manifest

**Release:** AFET-1.0 — General Field Entropy Theory
**Datum:** 2026-02-15
**Status:** release-ready
**Basislinie:** v12.0.0 (main)
**DOI-Sequenz:** 10.5281/zenodo.17472834 bis 10.5281/zenodo.18647936 (38 Publikationen)

---

## Logistic State

| Parameter | Wert | Interpretation |
|-----------|------|---------------|
| R | 0.78 | Fortschritt weit uber Schwelle |
| Theta | 0.56 | Release-Schwelle |
| beta | 4.8 | Informationsdomane |
| zeta(R) | 0.09 | Niedrige Impedanz |
| sigma | 0.73 | Release-resonant |

---

## Kernkonstanten

| Konstante | Symbol | Wert | Funktion |
|-----------|--------|------|----------|
| Metastabilitaetspuffer | sigma_Phi | 0.0625 (1/16) | Existenztoleranz |
| Skalierungsfaktor | Phi | 1.174 | Fraktale beta-Hierarchie |
| Integrationsgeschwindigkeit | v_RIG | 1.352 km/s | Kosmische Rendering-Rate |
| Kritische Dichte | S_crit | 16 | Frame-Principle-Schwelle |
| Feinstrukturkonstante | alpha^-1 | 137.036 | EM-Kopplungsstaerke |

---

## Validierungszusammenfassung

- **78 Datasets** uber 8 Domaenen validiert
- **Median r-squared:** 0.88 (88% Varianz erklaert)
- **Median Delta-AIC:** 12.1 (entscheidende Ueberlegenheit)
- **p < 0.001** durchgehend
- **Schluesselvorhersage:** 13.5 MHz Neurit-Resonanz (Fontana et al. 2024 bestaetigt)

---

## Artefakte

### Paper
| Datei | Rolle |
|-------|-------|
| `docs/AFET/AFET_Universal_Framework_Paper_final.md` | Hauptmanuskript (Markdown) |
| `docs/AFET/Afet universal framework paper final.pdf` | Hauptmanuskript (PDF) |

### Preprint
| Datei | Rolle |
|-------|-------|
| `docs/AFET/preprint_v12_consciousness.md` | v12 Bewusstseins-Erweiterung |

### Supplementary Materials
| Datei | Rolle |
|-------|-------|
| `docs/AFET/PERPLEXITY_INTEGRATION_SUMMARY.md` | Perplexity-Integration Changelog |
| `docs/AFET/Perplexity integration summary final.pdf` | Perplexity-Integration (PDF) |
| `docs/AFET/doi_citation_table.md` | Strukturierte DOI-Tabelle (38 DOIs) |

### Figuren (aus paper/)
| Datei | Rolle |
|-------|-------|
| `paper/figure1_utac_overview.pdf` | UTAC-Framework-Uebersicht |
| `paper/figure2_rg_derivation.pdf` | RG-Herleitung |
| `paper/figure3_abm_results.pdf` | ABM-Ergebnisse |
| `paper/figure4_meta_regression.pdf` | Meta-Regression |
| `paper/figure5_phi_scaling.pdf` | Phi-Skalierung |
| `paper/figure6_beta_by_field_type.png` | Beta nach Feldtyp |
| `paper/figure7_beta_outlier_analysis.png` | Beta-Ausreisser-Analyse |
| `docs/AFET/f87ed29c-b329-4429-afb2-ff3a21d68c6a.jpg` | AFET-Konzeptdiagramm |

### Quellmaterial
| Ordner | Rolle |
|--------|-------|
| `docs/AFET/` | Forensischer Intake-Ordner (19 Rohquellen) |
| `models/` | UTAC/AFET-Modellimplementierungen |
| `analysis/` | Validierungs- und Analyseskripte |
| `paper/generate_all_figures.py` | Reproduzierbare Figurenerzeugung |

---

## Zenodo-Konfiguration

- **Upload-Typ:** publication (workingpaper)
- **DOI-Konzept:** 10.5281/zenodo.17472834
- **Lizenz Code:** GPL-3.0
- **Lizenz Inhalt:** CC BY-NC 4.0

---

## Finalisierungs-Checkliste

- [x] Paper-Manuskript existiert (MD + PDF)
- [x] DOI-Citationstabelle vollstaendig (38 DOIs)
- [x] Intake-Register Trilayer synchronisiert
- [x] Figuren referenziert aus paper/
- [x] .zenodo.json aktualisiert
- [x] CITATION.cff aktualisiert
- [ ] Consent-Checkpoint vor Veroeffentlichung
