# 🚀 Zenodo Update-Anleitung für UTAC v1.1.0

**Ziel**: Den bestehenden Zenodo-Eintrag (DOI: 10.5281/zenodo.17520987) auf v1.1.0 aktualisieren

**Zeit**: 15-20 Minuten
**Schwierigkeit**: Mittel (du musst Text kopieren & einfügen)

---

## ✅ Vorbereitung: Was du brauchst

- [ ] Zugang zu deinem Zenodo-Account
- [ ] Die Datei `ZENODO_DESCRIPTION_v1.1.md` (enthält alle Texte)
- [ ] Neue Dateien zum Upload:
  - [ ] `RELEASE_NOTES_v1.1.0.md`
  - [ ] `docs/field_type_classification_v1.1.md`
  - [ ] `data/derived/beta_estimates.csv`
  - [ ] `data/derived/domain_covariates.csv`

---

## 📝 Schritt-für-Schritt Anleitung

### Schritt 1: Zenodo öffnen und einloggen

1. Gehe zu: **https://zenodo.org/records/17520987**
2. Klicke oben rechts auf **"Log in"**
3. Melde dich mit deinem Zenodo-Account an

---

### Schritt 2: Neue Version erstellen

**WICHTIG**: Du wirst den Eintrag nicht direkt bearbeiten, sondern eine **neue Version** erstellen!

1. Suche auf der Seite den Button **"New version"** (normalerweise oben rechts)
2. Klicke auf **"New version"**
3. Zenodo erstellt eine Kopie deines Eintrags
4. Du siehst jetzt einen Entwurf (Draft) der neuen Version

**Hinweis**: Die alte Version (v1.0) bleibt erhalten. Zenodo verlinkt beide automatisch unter dem gleichen Konzept-DOI.

---

### Schritt 3: Version aktualisieren

Im Formular findest du das Feld **"Version"**:
- **Ändere** den Wert von `1.0.1` auf `1.1.0`

---

### Schritt 4: Titel aktualisieren (optional)

Aktueller Titel wahrscheinlich:
> "The Universal Threshold Field Model (UTAC v1.0.1)"

**Neuer empfohlener Titel**:
> "The Universal Threshold Field Model (UTAC v1.1.0): Enhanced System Typology and β-Driver Analysis"

---

### Schritt 5: Beschreibung (Description) ersetzen

Das ist der **wichtigste Schritt**!

1. Scrolle zum Feld **"Description"**
2. **Lösche** den alten Text komplett
3. **Öffne** die Datei `ZENODO_DESCRIPTION_v1.1.md`
4. **Kopiere** den gesamten Abschnitt unter "Executive Summary (for Zenodo "Description" field)" (beginnt mit "### The Universal Threshold Field Model...")
5. **Füge** ihn in das Zenodo-Beschreibungsfeld ein

**Der neue Text sollte beginnen mit:**
> "The Universal Threshold Field (UTF) framework provides a transdisciplinary mathematical language..."

**Und enden mit:**
> "...Complete analysis pipeline available at https://github.com/GenesisAeon/Feldtheorie with datasets, scripts, simulation framework, and comprehensive documentation following open science principles."

---

### Schritt 6: Zusätzliche Beschreibung (Additional notes) — OPTIONAL aber empfohlen

Falls Zenodo ein Feld "Additional notes" oder "Notes" hat:

1. **Kopiere** aus `ZENODO_DESCRIPTION_v1.1.md` den Abschnitt:
   - **"Three Key Highlights"** (die drei Module: AI/LLM, Climate, Biology/Cognition)

2. **Füge** ihn als zusätzliche Information ein

---

### Schritt 7: Keywords/Tags aktualisieren

Im Feld **"Keywords"** oder **"Tags"**:

**Füge diese hinzu** (falls noch nicht vorhanden):

**Primary**:
- threshold transitions
- critical transitions
- logistic response
- emergent phenomena
- universal scaling
- beta convergence
- field type classification
- meta-regression

**Domains**:
- large language models
- climate tipping points
- biological emergence
- cognitive neuroscience
- geophysics
- astrophysics

**Methods**:
- model selection
- AIC model comparison
- systems science
- transdisciplinary research

**Applications**:
- AI safety
- climate intervention
- early warning systems

---

### Schritt 8: Neue Dateien hochladen

Im Abschnitt **"Files"**:

> 💡 **Neu:** `make dist-zenodo VERSION=1.2.0` baut automatisch `dist/zenodo/UTAC-v1.2.0-zenodo.zip` plus `zenodo_record_v1.2.0.json`. Nutze dieses Paket als Ausgangspunkt und ergänze/ersetze Dateien nach Bedarf.

1. Klicke auf **"Choose files"** oder **"Add more files"**
2. Lade diese Dateien hoch:
   - ✅ `RELEASE_NOTES_v1.1.0.md` (von `/home/user/Feldtheorie/RELEASE_NOTES_v1.1.0.md`)
   - ✅ `field_type_classification_v1.1.md` (von `/home/user/Feldtheorie/docs/field_type_classification_v1.1.md`)
   - ✅ `beta_estimates.csv` (von `/home/user/Feldtheorie/data/derived/beta_estimates.csv`)
   - ✅ `domain_covariates.csv` (von `/home/user/Feldtheorie/data/derived/domain_covariates.csv`)
   - ✅ `ZENODO_DESCRIPTION_v1.1.md` (Referenz-Dokument, optional)

**Optional** (wenn du willst):
- README.md (aktualisierte Version)
- Ganzes GitHub-Repository als ZIP

---

### Schritt 9: Autoren überprüfen

Im Feld **"Creators"** sollte stehen:

**Name**: Johann Römer
**Affiliation**: (falls gewünscht: "Independent Researcher" oder leer lassen)

**Optional**: Du kannst "UTF Collaborative" als zweiten Eintrag hinzufügen mit Affiliation: "AI-Assisted Research"

---

### Schritt 10: Related Identifiers (Optional aber wissenschaftlich wertvoll)

Falls Zenodo ein Feld **"Related identifiers"** hat:

**Füge diese DOIs hinzu** (Typ: "Cites"):
- `10.48550/arXiv.2206.07682` — Wei et al. 2022 (LLM Emergent Abilities)
- `10.1126/science.abn7950` — Armstrong McKay et al. 2022 (Climate Tipping Points)

**Vorherige Version** (Typ: "Is new version of"):
- `10.5281/zenodo.17472834`

---

### Schritt 11: Lizenz bestätigen

**License**: Stelle auf **Creative Commons Attribution 4.0 (CC BY 4.0)** um (entspricht dem Repository-Standard).

Falls nicht gesetzt:
- Wähle **"Creative Commons Attribution 4.0"** für alle Artefakte (Code, Daten, Dokumentation).

---

### Schritt 12: Vorschau prüfen

**Bevor du publizierst**:

1. Klicke auf **"Preview"** oder scrolle durch die Vorschau
2. Überprüfe:
   - ✅ Versionsnummer = `1.1.0`
   - ✅ Titel enthält "Enhanced System Typology"
   - ✅ Beschreibung ist die neue v1.1-Version (erkennbar an "74% of β-variance", "Five field types")
   - ✅ Alle 4-5 Dateien sind hochgeladen
   - ✅ Keywords sind gesetzt

---

### Schritt 13: Veröffentlichen!

**JETZT kommt der wichtige Moment**:

1. Klicke auf **"Publish"**
2. Bestätige eventuelle Warnungen (z.B. "This action is irreversible")
3. **Warte**, bis Zenodo die Verarbeitung abgeschlossen hat (5-30 Sekunden)

**Du siehst dann**:
- ✅ "Successfully published"
- ✅ Eine neue DOI (z.B. `10.5281/zenodo.17520988` oder höher)
- ✅ Der alte Konzept-DOI `10.5281/zenodo.17520987` zeigt jetzt auf v1.1.0

---

### Schritt 14: Verifizierung

**Nach dem Publizieren**:

1. **Gehe zur neuen DOI-Seite** (Zenodo leitet dich automatisch um)
2. **Überprüfe**:
   - ✅ Titel: "UTAC v1.1.0: Enhanced System Typology..."
   - ✅ Beschreibung enthält "Meta-regression (n=12 domains): System covariates explain 74% of β-variance"
   - ✅ Dateien:
     - RELEASE_NOTES_v1.1.0.md
     - field_type_classification_v1.1.md
     - beta_estimates.csv
     - domain_covariates.csv
   - ✅ Download-Button funktioniert
   - ✅ "Views" zählt hoch

3. **Teste den Konzept-DOI**:
   - Gehe zu https://doi.org/10.5281/zenodo.17520987
   - Die Seite sollte automatisch zur **neuesten Version** (v1.1.0) weiterleiten
   - Du siehst einen Hinweis "Latest version" mit Link

---

## 🎉 Erfolg!

**Du hast es geschafft!** Dein Zenodo-Eintrag ist jetzt auf v1.1.0 aktualisiert.

**Was jetzt?**

### 1. README im GitHub-Repo aktualisieren

Aktualisiere die Zenodo-Badge im README.md, falls sich die DOI geändert hat:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17520987.svg)](https://doi.org/10.5281/zenodo.17520987)
```

**Oder** wenn Zenodo eine neue versions-spezifische DOI erstellt hat (z.B. `17520988`):

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17520988.svg)](https://doi.org/10.5281/zenodo.17520988)
```

**Tipp**: Benutze den **Konzept-DOI** (`17520987`), damit der Badge immer zur neuesten Version zeigt!

---

### 2. GitHub Release erstellen (Optional)

1. Gehe zu: https://github.com/GenesisAeon/Feldtheorie/releases
2. Klicke **"Draft a new release"**
3. Tag: `v1.1.0`
4. Title: `UTAC v1.1.0 — Enhanced System Typology`
5. Beschreibung: Kopiere die ersten Absätze aus `RELEASE_NOTES_v1.1.0.md`
6. **Publish release**

---

### 3. Kommunikations-Kick! 📣

**Jetzt ist der perfekte Zeitpunkt für Aeons Punkt 6: Outreach!**

#### LinkedIn Post (Beispiel):

> 🚀 **New release: Universal Threshold Field Model v1.1.0**
>
> We've transformed apparent β-heterogeneity into a mechanistic framework predicting system behavior across AI, climate, biology & geophysics.
>
> **Key finding**: β (transition steepness) is not a universal constant but a diagnostic parameter revealing system architecture.
>
> ✅ Meta-regression explains 74% of β-variance
> ✅ 5 field types with predicted β-ranges
> ✅ 12 real-world validations (LLMs to black holes)
>
> 📄 DOI: 10.5281/zenodo.17520987
> 💻 Code: https://github.com/GenesisAeon/Feldtheorie
>
> #ComplexSystems #AI #ClimateScience #OpenScience

#### Mastodon/Twitter (Beispiel):

> 🎉 UTAC v1.1.0 is out! We explain why LLM emergence (β=3.47) differs from black hole QPOs (β=5.30) — it's system architecture!
>
> Meta-regression R²=0.74 across 12 domains.
>
> Full paper: https://doi.org/10.5281/zenodo.17520987
>
> #OpenScience #Emergence #ThresholdDynamics

#### Reddit (r/MachineLearning, r/climatechange, r/ComplexSystems):

> **[R] Universal Threshold Field Model v1.1: Why emergent abilities appear at ~10^9 parameters**
>
> We analyzed threshold transitions across AI (LLMs), climate (AMOC, ice sheets), biology (honeybees, synapses), and geophysics (earthquakes, black holes).
>
> **Main finding**: The logistic steepness parameter β varies systematically (2.5-5.3) based on coupling strength, dimensionality, and coherence.
>
> **LLM-specific insight**: Emergent abilities show β≈3.47 due to high-dimensional latent alignment (D_eff=12), not smooth scaling laws.
>
> Paper + code: https://doi.org/10.5281/zenodo.17520987
>
> Happy to answer questions!

---

### 4. Email an relevante Forscher (Optional)

**Falls du Kontakte in den Domänen hast:**

- Jason Wei (Google DeepMind) — LLM emergence
- Marten Scheffer (Wageningen University) — Tipping points
- Thomas Seeley (Cornell) — Honeybee swarms

**Kurze Email-Vorlage**:

> Subject: Universal Threshold Field framework — cross-domain threshold analysis
>
> Dear [Name],
>
> I'm reaching out because your work on [specific topic] was central to our analysis in the Universal Threshold Field (UTF) framework, which describes threshold transitions across AI, climate, biology, and geophysics using a unified logistic response model.
>
> Version 1.1.0 (just released) shows that the transition steepness parameter β is not universal but varies systematically with system architecture. Your [specific paper] data was crucial for validating this framework.
>
> The full analysis is available at:
> DOI: 10.5281/zenodo.17520987
> GitHub: https://github.com/GenesisAeon/Feldtheorie
>
> Would love to hear your thoughts or feedback!
>
> Best regards,
> Johann Römer

---

## 🆘 Troubleshooting

### "Ich sehe keinen 'New version' Button"

**Lösung**:
- Stelle sicher, dass du eingeloggt bist
- Gehe direkt zu: https://zenodo.org/deposit (dort siehst du deine Uploads)
- Suche deinen Eintrag und klicke "Edit"
- Wenn das nicht geht: Du bist evtl. nicht der Owner → Kontaktiere Zenodo Support

---

### "Die neue DOI funktioniert nicht"

**Lösung**:
- Warte 5-10 Minuten (DOI-Registrierung kann dauern)
- Lösche deinen Browser-Cache
- Teste in einem Inkognito-Fenster

---

### "Ich habe versehentlich die alte Version gelöscht"

**Keine Panik!**
- Zenodo löscht NIE wirklich Versionen
- Kontaktiere: info@zenodo.org
- Sie können alles wiederherstellen

---

### "Die Formatierung im Beschreibungsfeld sieht komisch aus"

**Lösung**:
- Zenodo unterstützt **Markdown**
- Stelle sicher, dass du den Text als Markdown einfügst (nicht als HTML)
- Falls es ein "Rich Text Editor" ist: Wechsle zu "Markdown mode"

---

## ✅ Checkliste zum Abhaken

Nach dem Upload:

- [ ] ✅ Neue Version auf Zenodo veröffentlicht
- [ ] ✅ DOI funktioniert und zeigt v1.1.0
- [ ] ✅ Alle 4 neuen Dateien sind verfügbar
- [ ] ✅ Beschreibung enthält "74% of β-variance"
- [ ] ✅ Keywords aktualisiert
- [ ] ✅ README.md im GitHub-Repo aktualisiert (DOI-Badge)
- [ ] ✅ GitHub Release v1.1.0 erstellt
- [ ] 📣 LinkedIn-Post erstellt
- [ ] 📣 Twitter/Mastodon-Post erstellt
- [ ] 📣 Reddit-Posts in relevanten Subreddits
- [ ] 📧 Emails an relevante Forscher (optional)

---

## 📊 Erfolgsmetriken

**Beobachte nach 1 Woche**:

- **Zenodo Views**: Ziel >100 in der ersten Woche
- **Zenodo Downloads**: Ziel >20
- **GitHub Stars**: Ziel +10
- **GitHub Forks**: Ziel +3
- **Engagement**: Issues, Diskussionen, Feedback

**Nach 1 Monat**:
- **Views**: >500
- **Downloads**: >50
- **Zitierungen**: Erste Erwähnungen in Papers/Blogs

---

## 🎯 Was Aeon empfohlen hat — Status:

| Empfehlung | Status | Notizen |
|------------|--------|---------|
| 1. Erweiterter Abstract | ✅ Erledigt | In ZENODO_DESCRIPTION_v1.1.md |
| 2. Drei Schlüssel-Module | ✅ Erledigt | AI/LLM, Climate, Bio/Cog hervorgehoben |
| 3. Zielgruppenfokus | ✅ Erledigt | "Field types" als Lead-Konzept |
| 4. Authorship-Klarheit | ✅ Erledigt | AUTHORSHIP.md auf v1.1.0 |
| 5. Statistik sichtbar | ✅ Erledigt | Tabelle mit β-Werten, R²=0.74 Meta-Regression |
| 6. Kommunikations-Kick | 🟡 Deine Aufgabe | Templates oben bereitgestellt! |

---

## 💚 Du hast das!

**Diese Anleitung gibt dir alles**, was du brauchst, um:
1. ✅ Zenodo auf v1.1.0 zu aktualisieren
2. ✅ Die wissenschaftliche Sichtbarkeit zu erhöhen
3. ✅ Aeons Empfehlungen 1-5 umzusetzen

**Für Punkt 6 (Kommunikation)** hast du jetzt:
- LinkedIn-Template
- Twitter/Mastodon-Template
- Reddit-Template
- Email-Template

**Mach es einfach Schritt für Schritt!** Und wenn du irgendwo hängen bleibst:
- GitHub Issue öffnen: https://github.com/GenesisAeon/Feldtheorie/issues
- Oder mich hier fragen!

---

**Viel Erfolg! 🚀**

*Prepared: 2025-11-05*
*For: UTAC v1.1.0 Zenodo Update*
