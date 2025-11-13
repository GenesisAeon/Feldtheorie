
# METHODS – UTAC Phase 2 (Microscopic Derivation of β from J/T)

**Ziel.** Wir untersuchen, ob der Steilheitsparameter **β** der UTAC-Übergangsfunktion nicht nur „Fit‑Konstante“, sondern **emergent** ist und sich aus einem **Kopplungs‑zu‑Rausch‑Verhältnis** **J/T** ableiten lässt. Dafür verwenden wir Agent‑basierte Modelle (ABMs) mit kontrollierten Nachbarschaftsregeln, Rauschmodellen und Gittergrößen sowie eine standardisierte Fit‑/Validierungs‑Pipeline.

## 1. Modellklasse und Update‑Regeln
- **Gitter**: quadratisches Lattice mit Größe *N×N*, *N ∈ {{64, 128, 256}}* (erweiterbar).
- **Nachbarschaft**: standardmäßig Moore‑Nachbarschaft (8‑Nachbarn), Varianten optional.
- **Zustände**: binär/reaktiv, mit probabilistischem Update.
- **Kopplung/Rauschen**: *J* (Kopplung) und *T* (Rauschen/Temperatur) werden als Verhältnis **R\_JT = J/T** variiert.
- **Rauschmodelle**: *gaussian*, *laplace*, *poisson* (Ablation → Robustheit).

## 2. Messgröße und Übergangsfunktion
Wir betrachten eine skalare Antwortgröße *y(R)* (z. B. Anteil aktivierter Agenten), als Funktion eines Kontrollparameters *R* (extern/effektiv). Übergänge werden mit einer logist. Kurve approximiert:
\[
\sigma(\beta\,(R-\Theta)) \;=\; \frac{1}{1+\exp\left[-\beta\,(R-\Theta)\right]} \,,
\]
wobei **β** die Steilheit und **Θ** die Schwelle ist.

## 3. Sweep‑Design
- **Seeds**: 10 Zufalls‑Seeds (*{{0,…,9}}*).
- **Lattice**: *N ∈ {{64,128,256}}*.
- **Rauschmodelle**: *gaussian*, *laplace*, *poisson*.
- **R\_JT**: *{{0.5, 1.0, 1.5, 2.0}}* (erweiterbar).
- **Läufen**: pro Konfiguration ein vollständiger Sweep über *R ∈ [0,1]* in gleichmäßigen Schritten.

## 4. Schätzung von β und Θ
- **Fit**: Nichtlineare Regression (bounded), Startwerte *β₀=4.0*, *Θ₀=Median(R)*, Grenzen *β∈[0.1,50]*.
- **Bootstrap‑KI**: 120 Resamples (mit Zurücklegen) auf Kurvenebene → *[β\_{2.5%}, β\_{97.5%}]*.
- **Ausreißer‑Robustheit**: Sortierung nach *R*, numerische Stabilisierung durch Clipping des Logits (*±60*).

## 5. Finite‑Size‑Scaling & Data‑Collapse
Für optionale Rohkurven (R,response) führen wir einen **Data‑Collapse** durch. Wir suchen Exponenten *(a,b)* und *R\_c*, so dass
\[
R' = (R - R_c)\,N^a,\qquad y' = y\,N^b
\]
über alle Kurven die mittlere Intra‑Bin‑Varianz minimiert. Minimierung via Nelder–Mead; Qualitätsmetrik: mittlere quadrierte Abweichung im Binning‑Raum.

## 6. Validierung
- **Seed‑Stabilität**: 10 Seeds pro Konfiguration → Verteilung von β.
- **Rausch‑Robustheit**: Vergleich der β(J/T)‑Beziehung über *gaussian/laplace/poisson*.
- **Finite‑Size‑Scaling**: β‑Shifts und Θ‑Shifts über *N*; optional Binder‑Kumulante bei verfügbarer 2./4. Momentik.
- **Cross‑Checks**: Sensitivität auf Nachbarschaft (Moore vs. von Neumann), Update‑Synchronität.

## 7. Statistik (Meta‑Ebene)
- **β vs. J/T**: linearisierte Regression *β ~ a·log(J/T) + b* (Alternativen: Potenz/FGLS).
- **Unsicherheit**: Bootstrap‑KIs auf Kurvenebene; Aggregation über Seeds/Lattice/Noise.
- **Mehrfachtests**: Holm/BH‑FDR in der Cross‑Domain‑Meta‑Analyse (siehe LIMITATIONS.md).

## 8. Reproduzierbarkeit
- **Make**: `make reproduce` (Validation → Aggregation → Plots).
- **Docker**: `docker build -t utac-validate . && docker run --rm -it -v $PWD:/app utac-validate`.
- **CI**: Seeds‑Matrix (10 Seeds) → Artefakte: CSV, JSON (roh+aggregiert), PNG‑Plots.
- **Entry‑Point**: via `RG_SIM_ENTRYPOINT="paket.modul:simulate"`; Stub‑Simulator verfügbar.

## 9. Software/Umgebung
- Python 3.11, NumPy, Pandas, SciPy, Matplotlib, Xarray/Dask/Zarr, fsspec.
- Betriebssystem‑agnostisch (Linux/Windows/macOS); CI: Ubuntu‑Runner.

## 10. Daten/Code & Zitation
- **Code**: `GenesisAeon/Feldtheorie` (UTAC Phase 2).
- **Daten**: erzeugte Resultate unter `analysis/results/` (CSV/JSON/PNG).
- **Zitation**: `CITATION.cff`; Attribution für OCF‑Inspiration (MIT) in `ACKNOWLEDGEMENTS.md`.

*Stand: 2025-11-13*
