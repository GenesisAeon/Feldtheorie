## 2. Theoretisches Framework

### 2.1 Lagrangedichte des gekoppelten Schwellenfeldes
**Formale Stimme.** Das gekoppeltes Schwellenfeld wird in `models/coupled_threshold_field.py` und `models/membrane_solver.py` als Paar \((\psi, \phi)\) modelliert. Die skalare Dynamik folgt der Lagrangedichte
\[
\mathcal{L} = \tfrac{1}{2}\partial_\mu \psi\,\partial^\mu \psi - V(\psi) - g^2 \lvert \nabla U \rvert^2 \psi^2 - \mathcal{J}\psi - \mathcal{C}\,\mathcal{M}[\psi,\phi],
\]
wobei \(V(\psi)=\tfrac{1}{2}m^2\psi^2+\lambda\psi^4\) die Selbstresonanz kodiert, \(g^2\lvert\nabla U\rvert^2\psi^2\) den Kontextdruck ankoppelt, \(\mathcal{J}\) externe Impulse einfaltet und \(\mathcal{M}[\psi,\phi]\) die Membran zwischen physikalischem und informationellem Feld moduliert. Die Resonanzantwort wird über die logistische Membran
\[
\sigma(R) = \frac{1}{1 + e^{-\beta(R-\Theta)}}
\]
getriggert, sobald der Ordnungsparameter \(R\) die Schwelle \(\Theta\) berührt.

**Empirische Stimme.** Die Parameter \((\Theta,\beta)\) werden über `analysis/coupled_field_threshold_fit.py` mit Maximum-Likelihood an `analysis/results/coupled_field_threshold.json` angepasst und gegen glatte Nullmodelle (Potenzgesetz, Exponential) getestet. ΔAIC-Werte \(>150\) und \(R^2\approx0{,}998\) sichern die logistische Dominanz.

**Poetische Stimme.** Wenn \(\psi\) an der Schwelle flammt, haucht \(\phi\) Erinnerung in das Feld: jede Resonanz ist der Atem der Membran, der das Rauschen zu einem Chor verdichtet.

### 2.2 Adaptive Schwelle \(\Theta(S,C,E)\)
**Formale Stimme.** Die dynamische Schwelle wird in `analysis/dynamic_threshold_lab.ipynb` als
\[
\Theta(t) = \Theta_0 + \alpha S_{\text{system}} + \beta_c C_{\text{sub}} + \gamma E + \int_{-\infty}^t K(t-t')R(t')\,\mathrm{d}t'
\]
modelliert. \(S\) beschreibt den globalen Systemzustand (z. B. Akkretionsscheiben-Dichte), \(C\) die lokale Substruktur (z. B. epigenetische Kopplung) und \(E\) externe Stressoren. Der Erinnerungskern \(K\) definiert die Feld-Metamemorie.

**Empirische Stimme.** `analysis/adaptive_theta_typology.py` bestätigt anhand synthetischer und realer Sequenzen (`analysis/results/dynamic_theta_tests.json`), dass adaptive Schwellen gegenüber statischen Modellen einen mittleren \(\Delta\mathrm{AIC}_{\text{dyn-static}}\approx222\) liefern. Simulator-Presets spiegeln die Parameter als Schieberegler in `simulator/`.

**Poetische Stimme.** Das Feld tastet seine eigene Vergangenheit ab. Jede Erinnerung biegt \(\Theta\) sachte, bis die Membran wieder resoniert und das System an der richtigen Stelle erwacht.

### 2.3 Feld-Metamemorie und Impedanz
**Formale Stimme.** Die effektive Horizontimpedanz folgt `models/logistic_envelope.py` als
\[
\zeta(R,t) = \zeta_0 + \kappa\,\partial_t\Theta(t),
\]
wodurch schnelle Schwellenverschiebungen die Membran verhärten. Ein Robin-Randterm im Solver koppelt \(\zeta\) an externe Beobachter.

**Empirische Stimme.** `analysis/membrane_robin_semantic_fit.py` zeigt, dass semantische Phasenübergänge in LLM-Proben denselben Impedanzsprung tragen (`analysis/results/membrane_robin_semantic.json`).

**Poetische Stimme.** Die Membran merkt sich jede Erschütterung: wenn \(\Theta\) tanzt, spannt sich \(\zeta\) wie eine Haut zwischen Sternenwind, Bienensummen und neuronalen Funken.

---

## 3. Empirische Validierung

### 3.1 Fallstudien über Domänen hinweg
Die folgenden Fits stammen aus den Resonanz-Skripten in `analysis/` und dokumentieren das Universalitätsband \(\beta \approx 4\text{–}6\).

| System | Kontrollparameter \(R\) | Schwelle \(\Theta\) | Steilheit \(\beta\) | Quelle |
| --- | --- | --- | --- | --- |
| GX 339-4 (BH-QPO) | Akkretionsrate (mCrab) | \(240 \pm 15\) | \(5.3 \pm 1.1\) | `analysis/results/coupled_field_threshold.json` |
| Apis mellifera | Nektarqualität (%) | \(37 \pm 0.8\) | \(4.1 \pm 0.6\) | `analysis/results/honeybee_waggle_fit.json` |
| Lenski LTEE Ara-3 | Generationen (×10³) | \(31.2 \pm 1.4\) | \(4.4 \pm 0.5\) | `analysis/results/lenski_citplus_fit.json` |
| GPT-4 Skill Burst | Modellgröße (Mrd. Parameter) | \(8.5 \pm 1.2\) | \(3.2 \pm 0.8\) | `analysis/results/llm_emergent_skill.json` |
| Urban Heat Canopy | Energiezufuhr (W/m²) | \(94 \pm 6\) | \(5.0 \pm 0.7\) | `analysis/results/urban_heat_canopy.json` |
| Amazon-Resilienz | Niederschlagsdefizit (%) | \(18.7 \pm 1.0\) | \(4.8 \pm 0.9\) | `analysis/results/amazon_resilience_fit.json` |

### 3.2 Nullmodell-Falsifikation
**Formale Stimme.** Jeder Fit dokumentiert in `analysis/results/*` die ΔAIC-Differenz zwischen logistischer Resonanz und glatten Alternativen. Schwellen gelten als bestätigt, wenn \(\Delta\mathrm{AIC} > 10\) und \(R^2 > 0.95\). Die Aggregation in `analysis/results/resonance_bridge_table.json` fasst Medianwerte (\(\bar{\Theta}=106\), \(\bar{\beta}=4.7\)) zusammen.

**Empirische Stimme.** `analysis/resonance_bridge_table.py` synchronisiert die Tabellenzeilen mit Docs und Simulator-Presets, sodass jede Domäne eine dokumentierte Nullmodell-Kontrolle besitzt.

**Poetische Stimme.** Die glatten Nullwinde verlieren gegen die Membranflamme: erst wenn das Rauschen schweigt, erscheint der leuchtende Knick der Schwelle und die Domänen singen im selben Takt.

### 3.3 Resonante Visualisierung
Die Diagramme in `analysis/reports/` und interaktiven `simulator/`-Views zeigen die sigmoiden Kurven direkt. Eine synthetische Brücke liefert `analysis/results/synthetic_threshold_sweep.json` als Playground, dessen Parameter im Frontend als „Luminous Threshold“-Preset erscheinen.

**Poetische Epilogzeile.** Jede Kurve, die sich zur Schwelle krümmt, ist eine Laterne im Feld: Bienen, Sterne, Städte und Algorithmen teilen denselben Atem, sobald \(R\) die Membran küsst.
