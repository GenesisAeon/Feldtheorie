# UTAC Falsifiability Framework

## Prüfrahmen und Testmethodik

Dieses Dokument definiert die **Falsifizierungskriterien** des Universal Threshold Adaptive Criticality (UTAC) Frameworks nach Karl Poppers Prinzipien wissenschaftlicher Überprüfbarkeit.

---

## 🎯 Kernprinzip: Falsifizierbarkeit

Eine wissenschaftliche Theorie ist nur dann wertvoll, wenn sie **falsifizierbar** ist – d.h., wenn es **klare empirische Kriterien** gibt, unter denen die Theorie als widerlegt gelten würde.

### UTAC-Haupthypothesen

**H₁ (Universalität des β-Werts)**:
```
Emergente Phasenübergänge in komplexen Systemen zeigen einen
Steilheitsparameter β im Bereich [3.6, 4.8] mit Zentralwert β̄ ≈ 4.2
```

**H₂ (Überlegenheit des Sigmoid-Modells)**:
```
Das logistische UTAC-Modell beschreibt Schwellenphänomene besser
als Nullmodelle (linear, exponentiell, konstant), gemessen via ΔAIC > 10
```

**H₃ (Feldkopplung als Mechanismus)**:
```
Die emergente Dynamik wird durch den Kopplungsterm M[ψ, φ] beschrieben
und ist experimentell manipulierbar
```

---

## ❌ Falsifizierungskriterien

### Kriterium 1: β außerhalb des Universalitätsbands

**Falsifikation erfolgt, wenn**:
- Ein klar definiertes Schwellenphänomen einen β-Wert **außerhalb [2.0, 7.0]** zeigt
- Mit statistischer Signifikanz p < 0.05
- Nach korrekter Anwendung der UTAC-Methodik

**Beispiel**: Wenn ein LLM-Emergenzphänomen zuverlässig β = 1.0 oder β = 10.0 zeigt, ist H₁ falsifiziert.

### Kriterium 2: Nullmodell überlegen

**Falsifikation erfolgt, wenn**:
- Ein Nullmodell (linear, exponentiell, konstant) bessere Vorhersagen liefert
- ΔAIC < 2 (d.h., Modelle sind äquivalent oder Nullmodell besser)
- Konsistent über mehrere Datensätze in derselben Domäne

**Beispiel**: Wenn lineare Skalierung AMOC-Kollaps besser beschreibt als Sigmoid (ΔAIC < 2), ist H₂ falsifiziert.

### Kriterium 3: Manipulationsexperiment scheitert

**Falsifikation erfolgt, wenn**:
- Manipulation des Kopplungsterms M[ψ, φ] keine vorhersagbaren Effekte zeigt
- Context-Gate ζ(R) experimentell nicht nachweisbar ist
- Simulationen keine plausiblen Schwellendynamiken reproduzieren

**Beispiel**: Wenn LLM-Alignment (Manipulation von M) keinen Einfluss auf Emergenz-Schwellen zeigt, ist H₃ geschwächt.

---

## 🧪 Experimentelle Validierung

### 1. Delta-AIC-Methode

**Vergleich UTAC vs. Nullmodelle**:

```python
from sklearn.metrics import log_loss
import numpy as np

# UTAC-Modell (logistisch)
def utac_model(R, beta, theta):
    return 1 / (1 + np.exp(-beta * (R - theta)))

# Nullmodell 1: Linear
def linear_model(R, a, b):
    return a * R + b

# Nullmodell 2: Exponentiell
def exp_model(R, a, b):
    return a * np.exp(b * R)

# AIC berechnen
def compute_AIC(y_true, y_pred, k):
    """
    k: Anzahl der Parameter
    """
    likelihood = -log_loss(y_true, y_pred, normalize=False)
    return 2 * k - 2 * likelihood

# Modelle fitten und vergleichen
# ... (siehe METRICS.md für Details)

delta_AIC = AIC_null - AIC_utac
```

**Akzeptanzkriterium**: ΔAIC > 10 für starke Evidenz

### 2. Bootstrap-Konfidenzintervalle

**Robustheit der β-Schätzung**:

```python
import numpy as np
from scipy.optimize import curve_fit

def bootstrap_beta(x, y, n_iterations=1000, seed=42):
    """
    Bootstrap-Schätzung von β mit Konfidenzintervallen
    """
    np.random.seed(seed)
    beta_samples = []

    for i in range(n_iterations):
        # Resample mit Zurücklegen
        indices = np.random.choice(len(x), len(x), replace=True)
        x_boot = x[indices]
        y_boot = y[indices]

        # Fit
        params, _ = curve_fit(utac_model, x_boot, y_boot, p0=[4.2, np.median(x)])
        beta_samples.append(params[0])

    # 95% CI
    ci_lower, ci_upper = np.percentile(beta_samples, [2.5, 97.5])

    return {
        'beta_mean': np.mean(beta_samples),
        'beta_std': np.std(beta_samples),
        'CI_95': [ci_lower, ci_upper]
    }
```

**Akzeptanzkriterium**: 95% CI überschneidet sich mit [3.6, 4.8]

### 3. Cross-Domain-Validierung

**Universalität testen**:

Für jede neue Domäne:
1. Identifiziere Schwellenphänomen
2. Sammle Daten (R vs. Emergenz-Metrik)
3. Fitte β und Θ
4. Prüfe: β ∈ [3.6, 4.8]?
5. Prüfe: ΔAIC > 10?

**Akzeptanzkriterium**: Mindestens 5 von 6 Domänen erfüllen beide Kriterien

---

## 📊 Fit-Kriterien und Güte-Maße

### R² (Bestimmtheitsmaß)

```python
from sklearn.metrics import r2_score

R2 = r2_score(y_true, y_pred_utac)
```

**Erwartung**: R² > 0.85 für guten Fit

### Root Mean Square Error (RMSE)

```python
RMSE = np.sqrt(np.mean((y_true - y_pred_utac)**2))
```

**Erwartung**: RMSE < 0.1 (für normalisierte Daten)

### Residuenanalyse

```python
residuals = y_true - y_pred_utac

# Normalität der Residuen (Shapiro-Wilk Test)
from scipy.stats import shapiro
stat, p_value = shapiro(residuals)

# Akzeptanz: p > 0.05 (Residuen normalverteilt)
```

---

## 🔬 Parameterbereiche und Hypothesentests

### Zulässige β-Bereiche

| Kategorie | β-Bereich | Interpretation |
|-----------|-----------|----------------|
| **Universell** | [3.6, 4.8] | Innerhalb UTAC-Universalitätsband |
| **Erweitert** | [2.0, 7.0] | Plausibel, aber außerhalb Kernband |
| **Falsifikation** | < 2.0 oder > 7.0 | UTAC nicht anwendbar |

### Θ-Plausibilitätsprüfung

Θ muss:
- Im physikalisch sinnvollen Bereich der Domäne liegen
- Mit unabhängigen Beobachtungen konsistent sein
- Nicht an den Rändern der Daten liegen (overfitting)

**Beispiel Klimadaten**: Θ = 1.5 °C ist plausibel (Paris-Abkommen, IPCC-Berichte), aber Θ = 50 °C wäre unplausibel.

---

## 🎲 Aufgabenbasierte Hypothesen

### LLM-Emergenz (Wei et al. 2022)

**Vorhersage**:
- Θ ≈ 8.5 × 10⁹ Parameter
- β ≈ 3.2 - 4.4
- ΔAIC > 10 vs. linearer Skalierung

**Falsifikation**: Wenn Chain-of-Thought bei 10⁷ Parametern oder 10¹² Parametern emergiert, aber nicht bei 10⁹.

### AMOC-Kollaps (Klimadaten)

**Vorhersage**:
- Θ ≈ 1.5 °C - 2.0 °C Erwärmung
- β ≈ 3.8 - 4.2
- Abrupter Übergang (innerhalb weniger Dekaden)

**Falsifikation**: Wenn AMOC linear mit Temperatur abnimmt ohne Schwelle.

### Bienenschwärme (Seeley 2010)

**Vorhersage**:
- Θ ≈ 150 Individuen
- β ≈ 3.9 - 4.3
- Synchronisation des Schwänzeltanzes

**Falsifikation**: Wenn Schwarmverhalten bei 50 oder 500 Individuen gleichermaßen auftritt.

---

## 🔍 Sensitivitätsanalysen

### Variation der Startwerte

Prüfe Robustheit des Fits gegenüber verschiedenen Initialisierungen:

```python
beta_estimates = []
for initial_beta in [2.0, 3.0, 4.0, 5.0, 6.0]:
    params, _ = curve_fit(utac_model, x, y, p0=[initial_beta, np.median(x)])
    beta_estimates.append(params[0])

# Konsistenz prüfen
beta_std = np.std(beta_estimates)
# Erwartung: std < 0.5
```

### Datenpunkte-Reduktion

Prüfe, wie viele Datenpunkte minimal nötig sind:

```python
for n_points in [10, 20, 50, 100, 200]:
    subset = np.random.choice(len(x), n_points, replace=False)
    x_sub = x[subset]
    y_sub = y[subset]
    # Fit und prüfe CI-Breite
```

**Erwartung**: Ab n ≥ 50 sollten stabile β-Schätzungen möglich sein.

---

## 🧮 Multiple Testing Correction

Bei Analyse mehrerer Domänen:

**Bonferroni-Korrektur**:
```
α_korrigiert = 0.05 / n_domains
```

Für n = 6 Domänen: α = 0.05 / 6 ≈ 0.0083

**Konservatives Kriterium**: Ein Befund ist nur signifikant, wenn p < 0.0083.

---

## ✅ Validierungs-Checkliste

### Für jede neue Domäne

- [ ] Schwellenphänomen klar definiert
- [ ] Daten gesammelt (R vs. Emergenz-Metrik)
- [ ] Datenqualität geprüft (Vollständigkeit, Ausreißer)
- [ ] β und Θ geschätzt mit Bootstrap-CI
- [ ] Nullmodelle gefittet (linear, exponentiell)
- [ ] ΔAIC berechnet
- [ ] β ∈ [3.6, 4.8]?
- [ ] ΔAIC > 10?
- [ ] R² > 0.85?
- [ ] Residuenanalyse durchgeführt
- [ ] Sensitivitätsanalyse bestanden
- [ ] Unabhängige Replikation (wenn möglich)

---

## 🚨 Warnsignale für Fehlinterpretation

### Overfitting

- **Symptom**: Perfekter Fit (R² > 0.99) bei wenigen Datenpunkten
- **Prüfung**: Cross-Validation
- **Akzeptanz**: Out-of-sample R² > 0.75

### Cherry-Picking

- **Symptom**: Nur positive Befunde publiziert
- **Schutz**: Prä-Registrierung von Hypothesen
- **Transparenz**: Negative Befunde ebenfalls berichten

### P-Hacking

- **Symptom**: p-Wert knapp unter 0.05
- **Schutz**: Konservative α-Level (Bonferroni)
- **Robustheit**: Multiple unabhängige Datensätze

---

## 📚 Präregistrierung und Open Science

### Empfohlenes Protokoll

1. **Vor der Datenanalyse**:
   - Hypothesen klar formulieren
   - Analysemethoden festlegen
   - Bei OSF oder AsPredicted registrieren

2. **Während der Analyse**:
   - Skripte versionieren (Git)
   - Alle Entscheidungen dokumentieren
   - Negative Befunde notieren

3. **Nach der Analyse**:
   - Daten und Code publizieren (Zenodo)
   - Abweichungen vom Präregistrierungsplan erklären
   - Replikationsanleitung bereitstellen

---

## 🔄 Replikationsstudien

### Interne Replikation

- Verschiedene Forscher im Team
- Unabhängige Code-Implementation
- Verschiedene Software (Python vs. R)

### Externe Replikation

- Unabhängige Forschergruppen
- Andere Datensätze derselben Domäne
- Cross-Cultural-Validierung (falls relevant)

**Goldstandard**: 3+ unabhängige Replikationen zeigen konsistente β-Werte.

---

## 🌍 Domänenspezifische Validierung

### LLMs

- **Daten**: Wei et al. (2022), Anthropic Reports, OpenAI Scaling Laws
- **Kriterium**: β ≈ 3.2 - 4.4, Θ ≈ 10⁹ Parameter
- **Replikation**: Analyse eigener LLM-Benchmarks

### Klima

- **Daten**: CMIP6, TIPMIP, Paleoklimatologie
- **Kriterium**: β ≈ 3.8 - 4.2, Θ ≈ 1.5 °C
- **Replikation**: Verschiedene Klimamodelle, historische Daten

### Biologie

- **Daten**: Seeley (Bienen), Katz (Synapsen), Lenski (E. coli)
- **Kriterium**: β ≈ 3.9 - 4.3, domänenspezifische Θ
- **Replikation**: Unabhängige Experimente, andere Spezies

---

## 📖 Zusammenfassung

UTAC ist **falsifizierbar** durch:

1. **β außerhalb [2.0, 7.0]** bei korrekter Methodik
2. **ΔAIC < 2** (Nullmodell mindestens so gut)
3. **Fehlende Reproduzierbarkeit** in unabhängigen Studien
4. **Manipulationsexperimente** zeigen keine vorhergesagten Effekte

**Aktueller Status**: Alle bisher untersuchten Domänen (n=6+) zeigen β ∈ [3.6, 4.8] mit ΔAIC > 10.

**Nächste Schritte**: Unabhängige Replikationen, neue Domänen, Manipulationsexperimente.

---

*Für Implementierungsdetails siehe [`../REPRODUCE.md`](../REPRODUCE.md)*
*Für theoretischen Hintergrund siehe [`utac_theory_core.md`](utac_theory_core.md)*
*Für Metriken siehe [`../METRICS.md`](../METRICS.md)*
