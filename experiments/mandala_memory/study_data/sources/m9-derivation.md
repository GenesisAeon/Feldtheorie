# M9: Warum das Mandala erinnert – Herleitung der Moden und eingefrorene Vorhersagen

Dieses Dokument ist **vor** jeder Rechnung an den zurückgehaltenen Parameterkombinationen geschrieben. Es leitet die Erinnerungsleistung des Netzes analytisch her, legt die Gedächtnisdauer ausdrücklich fest und beschreibt, wie die Vorhersagen eingefroren und geprüft werden.

**Auftrag (Johann, 2026-10-03):**
> Für M9 leite die Modul-Unterschieds- und Binnenmodul-Moden samt Geltungsbereich der Linearisierung her. Definiere Gedächtnisdauer ausdrücklich und berücksichtige Reizeinkopplung, Messoperator und Rauschen. Prüfe anschließend eingefrorene quantitative Vorhersagen an zurückgehaltenen Parameterkombinationen; dokumentiere den bisherigen Scan als Exploration.

Zusätzliche Hinweise aus demselben Auftrag:
- q ist nur eine obere Schranke; dasselbe q bedeutet keineswegs dieselbe Erinnerungsdauer.
- Neue Seeds allein machen die schon betrachtete deterministische Dynamik nicht zu einer unabhängigen Bestätigung.

## 1. Modellfamilie F (Geltungsbereich der Herleitung)

| Größe | Bereich |
|---|---|
| Knoten N, Module M | M teilt N; Modulgröße n = N/M ≥ 2, oder M = 1 (dann n = N) |
| Kopplung | A aus SCF `budget_adjacency`: A_ij = α = γ(1−c)/(n−1) innerhalb eines Moduls, β = γc/(N−n) zwischen Modulen, A_ii = 0. Bei M = 1 gilt A_ij = γ/(N−1). |
| Parameter | γ ∈ (0, 1), c ∈ [0, 1], ℓ ∈ (0, 1] |
| Reiz | Amplitude a > 0 auf Knoten i (Klasse A) bzw. j ≠ i (Klasse B), genau ein Pulsschritt aus x₀ = 0 |
| Nichtlinearität | tanh; identity als Grenzfall ohne Linearisierungsfehler |
| Ausgeschlossen | Eingriffe nach dem Reiz, Kantenablation, Hebb-Anpassung (alle brechen die unten benutzte Symmetrie oder Blockstruktur) |

Schritt: x_(k+1) = (1−ℓ) x_k + ℓ tanh(A x_k + B u_k). Ablesung bei Pause d ist x_(d+1), wie im Benchmark.

**Messung:** y = H x_(d+1) + ε mit ε ~ N(0, σ² I) auf jeder beobachteten Größe, gleiche Vorwahrscheinlichkeiten. Untersucht werden vier Messoperatoren H:

| H | Beschreibung | ‖H‖₂ |
|---|---|---|
| `full` | I_N, alle Knoten | 1 |
| `module_means` | M × N, Zeile m = 1_m / n | 1/√n |
| `sum` | 1ᵀ | √N |
| `node:r` | e_rᵀ, ein Knoten | 1 |

## 2. Reizeinkopplung ist exakt

Aus x₀ = 0 gilt A x₀ = 0, also x_1 = ℓ tanh(a) e_i. Für Klasse B steht dort e_j.

Die Reizstärke geht damit **exakt** als Faktor g := ℓ·tanh(a) in den Anfangsunterschied Δx_1 = g (e_i − e_j) ein. Die tanh-Sättigung beim Reiz ist hier vollständig berücksichtigt; linearisiert wird nur die Pause.

Im linearen Grenzfall (identity) gilt g = ℓ·a. Ein Entwicklungstest hat gezeigt, dass meine erste Fassung des Vorhersagemoduls auch dort ℓ·tanh(a) benutzte. Das ist korrigiert; die Prüfkombinationen sind ohnehin alle tanh.

## 3. Moden der Pause (linearer Teil)

In der Pause ist u = 0 und 0 ein Fixpunkt. Die Linearisierung lautet J = (1−ℓ) I + ℓ A.

A ist symmetrisch, weil alle Module gleich groß sind, und hat drei Eigenräume. Die Probe ist die Spur von A: γ + (M−1)λ_D + (N−M)λ_I = 0 = tr A. Die Rechnung steht in `controls/m9_hand_controls.py`.

| Mode | Eigenraum | Dimension | Eigenwert von A | Eigenwert von J |
|---|---|---|---|---|
| **Gleichtakt** | 1 (alle gleich) | 1 | γ | **q = 1 − ℓ + ℓγ** |
| **Modul-Unterschied** | konstant je Modul, Gesamtsumme 0 | M − 1 | λ_D = α(n−1) − βn = γ(1 − cN/(N−n)) | **μ_D = 1 − ℓ + ℓγ(1 − cN/(N−n))** |
| **Binnenmodul** | Summe 0 innerhalb jedes Moduls | N − M | λ_I = −α = −γ(1−c)/(n−1) | **μ_I = 1 − ℓ − ℓγ(1−c)/(n−1)** |

Bei M = 1 entfällt der Modul-Unterschied, und es gilt λ_I = −γ/(N−1).

**Benchmark** (N = 12, M = 3, c = 1/4, γ = 4/5, ℓ = 1/2), exakt: q = 9/10, μ_D = 3/4, μ_I = 2/5.

### Projektion des Reizunterschieds

Für u = e_i − e_j:

- **Gleichtakt-Anteil:** immer 0, denn 1ᵀu = 0.
- **i und j in verschiedenen Modulen m_i ≠ m_j:**
  - P_D u = (1_{m_i} − 1_{m_j})/n mit ‖P_D u‖² = 2/n;
  - P_I u = u − P_D u mit ‖P_I u‖² = 2 − 2/n.
- **i und j im selben Modul:** P_D u = 0, P_I u = u, ‖P_I u‖² = 2.

Linear vorhergesagt:

  Δx_lin(d) = g·[ μ_D^d · P_D u + μ_I^d · P_I u ]

### Strukturelle Folgerungen

- **(S1) q ist nicht die Erinnerungsrate.** Der Reizunterschied hat keinen Gleichtakt-Anteil, und zwar auch im nichtlinearen Modell (Abschnitt 5). q begrenzt die Abklingrate nur nach oben: Es gilt |μ_D|, |μ_I| ≤ q, mit μ_D = q nur bei c = 0. Netze mit gleichem q erinnern deshalb verschieden lang, je nach c, n und Eingangslage.
- **(S2) Abschottung hält, Vermischung löscht.** Für c < (N−n)/N ist μ_D > 1 − ℓ; wächst c, sinkt μ_D. Ab c > (N−n)/N wird λ_D negativ (anti-modular), und die Spur wechselt das Vorzeichen.
- **(S3) Eingänge im selben Modul** tragen nur über μ_I, das klein oder negativ ist. Dort ist die Erinnerung kurz.
- **(S4) Messoperator:**
  - `module_means` sieht nur den Modul-Unterschied: ‖HΔx‖ = g·|μ_D|^d·√2/n bei verschiedenen Modulen, 0 im selben Modul.
  - `sum` sieht nichts, also gilt Bayes ≡ 1/2.
  - `node:r` sieht eine einzelne Komponente; sie kann bei μ_I < 0 das Vorzeichen wechseln und ist dann nicht monoton.
- **(S5) Reiz und Rauschen:** Im linearen Teil gehen a und σ nur über g/σ = ℓ tanh(a)/σ ein. Die tanh-Sättigung beim Reiz begrenzt den Gewinn durch größere Reize auf den Faktor ℓ.

## 4. Gedächtnisdauer (Definition)

**Ideale Trefferquote:**

  Bayes(d) = Φ( ‖H Δx(d)‖₂ / (2σ) )

Das ist die optimale Trefferquote für zwei Normalverteilungen mit gleicher Kovarianz σ²I und gleichen Vorwahrscheinlichkeiten. Ein trainierter Decoder mit endlich vielen Beispielen liegt im Erwartungswert darunter.

**Gedächtnisdauer D_p\*** für die Schwelle p\* = 0,75:

  D = max{ d ∈ {0, …, 64} : Bayes(d) ≥ p\* }

Sonderfälle:
- **„keine“:** schon Bayes(0) < p\*.
- **zensiert:** Bayes(64) ≥ p\*.

Gleichwertig gilt ‖HΔx(d)‖ ≥ r\* := 2σ·Φ⁻¹(p\*). Bei p\* = 0,75 ist Φ⁻¹(p\*) = 0,67449.

**Näherung für einen dominanten Modus** (`full`, verschiedene Module, |μ_I| ≪ |μ_D|):

  D ≈ ⌊ ln( g·√(2/n) / r\* ) / ln(1/|μ_D|) ⌋

Die Dauer wächst also mit 1/ln(1/|μ_D|), nicht mit q, und nur logarithmisch mit Reizstärke/Rauschen. Vorhergesagt wird aber nicht diese Näherung, sondern die exakte lineare Kurve samt Fehlerschranke (Abschnitt 5).

## 5. Geltungsbereich der Linearisierung: beweisbare Fehlerschranke

**Symmetrie.** Für jedes Paar i ≠ j in F gibt es eine Permutation P mit P² = I, P e_i = e_j und P A Pᵀ = A:
- **i, j im selben Modul:** die Transposition (i j).
- **Verschiedene Module:** P tauscht die Module m_i und m_j positionsweise, (m_i, t) ↔ (m_j, π(t)). Dabei ist π die Transposition der Modulpositionen von i und j, oder die Identität, wenn diese gleich sind.

Weil die Dynamik mit P vertauscht und x_1^B = P x_1^A, gilt **für alle k**: x_B(k) = P x_A(k).

Damit liegt Δx(k) = (I − P) x_A(k) im antisymmetrischen Raum V₋ = {v : Pv = −v}:
- 1 liegt nicht in V₋; das beweist (S1) auch nichtlinear.
- J lässt V₋ invariant, und auf V₋ gilt ‖J^m v‖₂ ≤ ρ^m ‖v‖₂ mit ρ = max(|μ_D|, |μ_I|), im selben Modul ρ = |μ_I|.

**Fehlerrekursion.** Sei e_k = Δx(k) − Δx_lin(k); dabei ist e_1 = 0. Mit z_k = A x_A(k) und h(z) = z − tanh z gilt

  e_(k+1) = J e_k − ℓ [ h(z_k) − P h(z_k) ],

und der Klammerterm liegt in V₋.

**Monotone Majorante.** Wegen A ≥ 0 und 0 ≤ tanh(z) ≤ z für z ≥ 0 gilt per Induktion komponentenweise 0 ≤ x_A(k) ≤ y_k := J^(k−1) x_1. Die Voraussetzung dafür ist 1 − ℓ ≥ 0. Weil h auf [0, ∞) wächst, folgt 0 ≤ h(z_k) ≤ h(A y_k). Damit

  ‖e_(d+1)‖₂ ≤ E(d) := 2ℓ · Σ_(k=1..d) ρ^(d−k) · ‖h(A y_k)‖₂ .

y_k ist geschlossen bekannt, ohne Simulation:

  J^(k−1) e_i = q^(k−1)·1/N + μ_D^(k−1)·(1_{m_i}/n − 1/N) + μ_I^(k−1)·(e_i − 1_{m_i}/n)

**Vorhersageband.** Mit s_lin(d) = ‖H Δx_lin(d)‖ gilt beweisbar

  Bayes(d) ∈ [ Φ(max(0, s_lin − ‖H‖₂E)/2σ),  Φ((s_lin + ‖H‖₂E)/2σ) ].

Für D folgt D ∈ [D_lo, D_hi]:
- D_lo ist die letzte Pause, bei der die **untere** Bandgrenze ≥ p\* ist;
- D_hi ist die letzte Pause, bei der die **obere** Bandgrenze ≥ p\* ist.

Ist E klein gegen s_lin (kleine Reize, kleines ℓγ), ist das Band schmal und D_lo = D_hi. Bei starken Reizen kann es breit werden. Das ist dann eine ehrliche, schwache Vorhersage und kein Versagen.

**Kleinsignal-Kennzahl** (nur beschreibend): κ_nl = γ·ℓ·tanh(a). Sie ist eine obere Grenze für |A x_1|_∞ bezogen auf die tanh-Krümmung.

## 6. Vorhersagen, die eingefroren werden

Für jede zurückgehaltene Kombination h (Abschnitt 7) wird **vor** jeder Rechnung mit dem Kern festgehalten:

1. μ_P = q, μ_D, μ_I, ρ, Projektionsgewichte, g, ‖H‖₂, κ_nl.
2. Für jedes d = 0…64: s_lin(d), E(d), das Bayes-Band [lo(d), hi(d)] und der lineare Punktwert.
3. D_lin (aus der linearen Kurve), das Intervall [D_lo, D_hi] und der Vergleichswert D_q der „naiven q-Regel“ (Abklingen des Anfangsunterschieds mit q^d).

## 7. Prüfung

### Zurückgehaltene Kombinationen

- **Herkunft:** gezogen mit festem Seed aus einem Raster, dessen Werte für c, γ, ℓ, a und σ bei **keinem** bisher angesehenen Fall vorkamen.
- **Bisher angesehen:**
  - Benchmark;
  - das Wegwerf-Skript vor M8 (Liste in der Roadmap);
  - alle Einträge in `explore/protocol.jsonl`;
  - die Entwicklungsfälle der M9-Tests.
- **Mechanische Prüfung beim Einfrieren:** Keine gezogene Kombination stimmt mit einem angesehenen Fall überein.
- **Umfang:** 24 Kombinationen, je 6 pro Messoperator. Etwa ein Drittel hat die Eingänge im selben Modul; bei M = 1 ist das immer so.

### Prüfstufen

**Primärprüfung (deterministisch, über die ganze deklarierte Menge).** Für jede Kombination und jedes d = 0…64 muss gelten:
- die Bayes-Kurve des getesteten Kerns liegt im eingefrorenen Band, mit Gleitkomma-Toleranz 1e‑12 relativ auf ‖HΔx‖;
- D des Kerns liegt in [D_lo, D_hi].

Eine einzige Verletzung **widerlegt** die Herleitung oder ihre Umsetzung. Sie wird berichtet und nicht stillschweigend repariert.

**Sekundärprüfung (Rauschen und Decoder, statistisch).** Für jede Kombination mit 0 ≤ D_lin ≤ 63, bei d = D_lin und d = D_lin + 1:
- Nearest-Mean-Decoder ohne Standardisierung, 1000 Trainings- und 4000 Testepisoden je Klasse, neue Seeds (Modus `m9`).
- Vorhergesagt: Balanced Accuracy ∈ [lo(d) − 0,01 − 4·SE, hi(d) + 4·SE] mit SE = √(p(1−p)/8000) und p = Bandmitte. Die 0,01 decken den Verlust durch geschätzte Klassenmittel; abgeschätzt ist er mit ≤ 0,003 für N ≤ 24 bei 1000 Beispielen je Klasse.

**Informativ, ohne Bestehensgrenze:**
- Anzahl der Kombinationen mit D_lo = D_hi (Punktvorhersage), Bandbreiten;
- Anzahl der Kombinationen, bei denen die naive q-Regel D falsch vorhersagt (D_q ∉ {D_Kern});
- **Zusatzhypothese Z1, nicht bewiesen:** Bei `full` und verschiedenen Modulen liegt die echte Trennung nie über der linearen (s_Kern ≤ s_lin). Begründung, nur heuristisch: Die tanh-Kompression trifft das stärker erregte Modul stärker. Z1 kann scheitern; das Ergebnis wird so oder so berichtet.

### Was ein Bestehen bedeutet und was nicht

| Ebene | evidence_kind | Bedeutung |
|---|---|---|
| Fehlerschranke | `analytic_argument` | ein Beweis für die ganze Familie F |
| Deklarierte Menge | `exhaustive_finite` | alle 24 × 65 Punkte geprüft |
| Übertragung auf F | `numerical_sample` | eine Stichprobe; sie ersetzt den Beweis nicht |

Weitere Einordnung:
- **Statistische Schicht:** `numerical_sample` / `synthetic_only`.
- **Keine Gewinnerbehauptung, keine biologische Aussage.**
- **Außerhalb von F** (Ablation, Eingriffe, Hebb-angepasste oder ungleich große Module) gilt nur die q-Schranke aus M8. Für diese Fälle wird **nichts** vorhergesagt.

## 8. Der bisherige Scan war Exploration

Die Tabelle vor M8 („Module abgeschotteter … c = 0,05 hält bei d = 8 noch 0,94“) und alle Läufe im Regler-Labor sind **explorativ**:
- Sie haben die Idee zu (S1)–(S3) geliefert.
- Sie sind keine Bestätigung davon.
- Ihre Kombinationen sind in M9 keine Prüffälle.
- Der Satz „fast dreimal so lange“ aus dieser Phase war ohne Schwelle formuliert und gilt als **zurückgezogen**. Mit der Definition aus Abschnitt 4 wird die Dauer für jede Prüfkombination neu und vorab bestimmt.
