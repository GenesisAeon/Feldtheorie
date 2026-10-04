# M11-Protokoll „Die vorhandene Erinnerung besser auslesen“ (Narrativ-Zwilling)

Trilayer: `m11_protokoll.json` (maßgeblich), `m11_protokoll.yaml` (Strukturzwilling), diese Datei (Erzählung); erzeugt mit `tools/make_trilayer_twins.py`.

- **Status:** candidate (step 2: development); NOT frozen; research references not computed
- **SHA-256 des JSON** (LF-normiert): `7dd73fccf4893fa3fd07adcdd2b172637ff5f5e8a6e2091c605333ce7dd4d68b`
- **Plan:** [`../docs/M11_PLAN_AUSLESE.md`](../docs/M11_PLAN_AUSLESE.md) (Fassung 2). Das Mandala ist unverändert (eingefrorene M10-Funktionen), d = 4, Aufgabe Bewahren.

| Fall | Netz | Bedingung | Rolle |
|---|---|---|---|
| modular_N | modular | N | main |
| uniform_Fplus | uniform | Fplus | secondary |
| modular_K0 | modular | K0 | control |
| uniform_K0 | uniform | K0 | control |

**Trainingsmengen:** [250, 1000, 4000, 16000] je Klasse (Präfixe einer Ziehung); Testpaare je Seed: 100000.

**Decoder:**
- Nearest-Mean, LDA (Ledoit-Wolf);
- MLP 12 → 32 tanh → 1 mit lr = 0.03, L2 = 0.001, Geduld 100, höchstens 3000 Epochen, 3 Initialisierungen. Die Hyperparameter wurden nur an Entwicklungsfällen nach der Validierungsregel gewählt; siehe `hyperparameter_selection_result`.

**Bestätigend:** C-Daten (Helfen mehr Beispiele LDA?) und C-Modell (MLP-Lernverfahren gegen LDA bei n = 1000), δ = 0.01, Holm α = 0.05, einseitiger t-Test (Normalannahme).

**Referenzen** (Bayes aus M10, NM(∞), LDA(∞), L_found) werden erst in der Referenzphase berechnet; siehe die Abschnitte `phases` und `linear_reference` im JSON.
