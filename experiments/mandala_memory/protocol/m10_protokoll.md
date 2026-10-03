# M10-Protokoll „Erinnerung unter Ablenkung“ (Narrativ-Zwilling)

Trilayer nach Feldtheorie `AGENTS.md`:

| Schicht | Datei | Rolle |
|---|---|---|
| JSON | `m10_protokoll.json` | maßgebliche Fassung |
| YAML | `m10_protokoll.yaml` | inhaltsgleicher Strukturzwilling |
| Markdown | diese Datei | Erzählung |

Die beiden Zwillinge sind aus dem JSON erzeugt (`tools/make_trilayer_twins.py`).

- **Status:** FROZEN 2026-10-03 after the final review ABSCHLUSSPRUEFUNG_6f2acfd.md; reviewed code commit 6f2acfd2a8a153c8f48bc50194cbcf651a510758; freeze record protocol/m10_freeze.json
- **SHA-256 des JSON** (LF-normiert): `84d2b523d5f4c7dc9acc8e91d1986d71306e9aedbd4f99ef74c35c5b2056c345`

Plan und Begründungen: [`../docs/M10_PLAN_ABLENKUNG.md`](../docs/M10_PLAN_ABLENKUNG.md) (Fassung 2).

**Netze:**
- modular: M = 3, c = 1/4;
- uniform: M = 1;
- beide mit N = 12, γ = 0,8, ℓ = 0,5, Zielknoten 0/4, a = 0,6, ohne Hebb;
- lineare Zwillinge zur Prüfung von A2/A3.

**Ablauf:**
- Zielreiz, Ruhe, dann ein Ablenkfenster W = 3 direkt vor der Ablesung (p = 0,5 je Schritt, X/Y je ½), danach Ablesung x_(d+1) mit σ = 0,02;
- Pausen d ∈ {3, 4, 6}, primär d = 4.

| Bedingung | Orte X / Y | Amplitude |
|---|---|---|
| K0 | – | – |
| F | 8 / 10 | 0.6 |
| N | 1 / 5 | 0.6 |
| Fplus | 8 / 10 | 1.8 |

**Ebene B** (Bayes, explizite Mischungs-Likelihood über 27 Fenstermuster):
- n_MC = 2,000,000 Ziehungen je Schätzung, Blöcke zu 50,000, eigener Strom je Schätzung;
- Aufgabe „letzter Kanal“: bedingt auf ≥ 1 Puls, Klassen X/Y gleich wahrscheinlich, K0 = N/A.

**Ebene D** (trainierte Decoder, **nur beschreibend**):
- 20 Seeds, je 1000 Trainings- und 2000 Testepisoden je Klasse;
- Nearest-Mean und LDA (Ledoit-Wolf).

**Bestätigend:**
- H-N, H-F+ auf Ebene B bei d = 4;
- einseitig, δ = 0.01, Holm α = 0.05;
- Z aus Monte-Carlo-Standardfehlern, SE = 0-Regel wie im JSON.

**Diagnosen:**
- A1 (Zustandsidentität) und A2 strukturell sind deterministisch.
- A2/A3 numerisch sind **statistische Alarme** (4 SE), keine sicheren Programmfehler; es gibt keine Wiederholung bis zum Bestehen.

**Ausschluss, Ressourcen, Smoke- und Entwicklungseinstellungen:** siehe JSON.
