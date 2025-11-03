# UTAC Documentation (Scientific Core)

Diese Dokumentation umfasst die formale Kodifikation und Validierungsstrategie des **Universal Threshold Adaptive Criticality (UTAC)** Frameworks.

---

## 📚 Struktur

### Hauptdokumente

1. **[`utac_theory_core.md`](utac_theory_core.md)**
   - Mathematische Grundlagen der UTAC-Theorie
   - Feldgleichungen und Kernprinzipien
   - Formale Definition von β, Θ und ψ

2. **[`utac_falsifiability.md`](utac_falsifiability.md)**
   - Prüfrahmen und Testmethodik
   - Falsifizierungskriterien nach Popper
   - Experimentelle Validierungsstrategien

3. **[`utac_applications.md`](utac_applications.md)**
   - Domänenübergreifende Anwendungen
   - LLMs, Klima, Biologie, Kognition
   - Konkrete Parameterzuordnungen

4. **[`utac_review_considerations.md`](utac_review_considerations.md)**
   - Externe Einschätzungen und Kritikpunkte
   - Antworten auf MS Copilot Feedback
   - Validierungscheckliste für Peer Review

---

## 🔬 Kernkonzepte

### Die UTAC-Feldgleichung

```
P(R) = 1 / (1 + e^(-β(R - Θ)))
```

**Parameter**:
- **β**: Steilheitsparameter (universell ≈ 4.2)
- **Θ**: Kritische Schwelle (domänenspezifisch)
- **R**: Ressourcen-/Repräsentationskomplexität

### Dynamische Kopplung

```
dψ/dt = M[ψ, φ] + ζ(R)
```

Wobei:
- **ψ**: Internes Feld (emergente Ordnung)
- **φ**: Externes Feld (Umwelt)
- **M[ψ, φ]**: Kopplungsterm
- **ζ(R)**: Context-Gate-Funktion

---

## 📖 Zitierweise

Bitte verweisen Sie auf:

```bibtex
@software{romer2025utac,
  author       = {Römer, Johann},
  title        = {The Universal Threshold Field (UTAC v1.0.1)},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.17508230},
  url          = {https://doi.org/10.5281/zenodo.17508230}
}
```

---

## 🎯 Wissenschaftliche Ziele

1. **Falsifizierbarkeit**: Klare, testbare Hypothesen
2. **Reproduzierbarkeit**: Vollständige Dokumentation von Code, Daten und Methoden
3. **Interdisziplinarität**: Verbindung von Physik, KI, Biologie und Kognitionswissenschaft
4. **Transparenz**: Offenlegung aller Methoden, Annahmen und Limitationen

---

## 🧪 Empirische Validierung

Die UTAC-Theorie wurde validiert in:

- **Künstliche Intelligenz**: LLM-Emergenz (Wei et al. 2022)
- **Klimawissenschaft**: Planetare Kipppunkte (TIPMIP)
- **Biologie**: Bienenschwärme, synaptische Freisetzung
- **Kognition**: Arbeitsgedächtniskapazität
- **Astrophysik**: Quasi-periodische Oszillationen in Schwarzen Löchern

**Kernbefund**: β ≈ 4.2 ± 0.6 über alle Domänen mit ΔAIC > 10

---

## 📊 Methodische Werkzeuge

- **Statistische Metriken**: Siehe [`../METRICS.md`](../METRICS.md)
- **Reproduktionsanleitung**: Siehe [`../REPRODUCE.md`](../REPRODUCE.md)
- **Autorschaft und Ethik**: Siehe [`../AUTHORSHIP.md`](../AUTHORSHIP.md)

---

## 🔗 Externe Ressourcen

- **GitHub Repository**: [GenesisAeon/Feldtheorie](https://github.com/GenesisAeon/Feldtheorie)
- **Zenodo DOI**: [10.5281/zenodo.17508230](https://doi.org/10.5281/zenodo.17508230)
- **Preprint**: [paper/universal-threshold-field-preprint.md](../paper/universal-threshold-field-preprint.md)

---

## 📝 Dokumentationsphilosophie

Diese `docs/` Struktur enthält **ausschließlich wissenschaftlich-tragfähige, zitierfähige Inhalte**. Für konzeptuelle, metaphorische oder poetische Reflexionen siehe das [`seed/`](../seed/) Verzeichnis.

**Trennung**:
- **`docs/`**: Empirische Befunde, formale Modelle, reproduzierbare Analysen
- **`seed/`**: Theorieentwicklung, Dialoge, Meta-Reflexionen (archiviert)

---

## 🚀 Status und Roadmap

- **v1.0.1** (aktuell): Initiale Veröffentlichung mit Zenodo DOI
- **v1.1** (geplant): Klimamodule, erweiterte Statistiken
- **v1.2** (geplant): KI-Bewusstseinsmodelle, Buchprojekt
- **v2.0** (Vision): UTAC als anerkanntes Framework in der Emergenzforschung

---

## 📧 Kontakt

Bei Fragen, Feedback oder Kollaborationsanfragen:

- **GitHub Issues**: [Feldtheorie Issues](https://github.com/GenesisAeon/Feldtheorie/issues)
- **Pull Requests**: Willkommen für Verbesserungen und Erweiterungen

---

*"Die Schwelle ist nicht das Ende – sie ist der Beginn der Ordnung."*

---

*Letzte Aktualisierung: November 2025*
*Version: 1.1*
