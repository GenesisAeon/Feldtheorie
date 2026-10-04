"""Trilayer twins (Feldtheorie AGENTS.md: YAML structure + JSON interface +
Markdown narrative) for the frozen M9 predictions.

The JSON stays the authoritative, hash-protected artifact and is only READ.
Written (overwriting only these generated twins):
    protocol/m9_frozen_predictions.yaml   same content as the JSON
    protocol/m9_frozen_predictions.md     short narrative + table

Floats are written so that YAML 1.1 loaders (PyYAML) read them back as the
same float: repr() mantissas without a decimal point get ".0" ("1e-18" would
otherwise load as a string).

    python experiments/mandala_memory/tools/make_trilayer_twins.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PROTOCOL = Path(__file__).resolve().parents[1] / "protocol"
SRC = PROTOCOL / "m9_frozen_predictions.json"


def yaml_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        r = repr(v)
        if "e" in r:
            mant, exp = r.split("e")
            if "." not in mant:
                mant += ".0"
            r = f"{mant}e{exp if exp[0] in '+-' else '+' + exp}"
        return r
    return json.dumps(v, ensure_ascii=False)


def yaml_dump(obj, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(obj, dict):
        if not obj:
            return pad + "{}"
        lines = []
        for k, v in obj.items():
            key = json.dumps(str(k), ensure_ascii=False)
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{key}:\n{yaml_dump(v, indent + 1)}")
            else:
                lines.append(f"{pad}{key}: {'{}' if v == {} else '[]' if v == [] else yaml_scalar(v)}")
        return "\n".join(lines)
    if isinstance(obj, list):
        if not obj:
            return pad + "[]"
        if all(not isinstance(v, (dict, list)) for v in obj):
            return f"{pad}[{', '.join(yaml_scalar(v) for v in obj)}]"
        return "\n".join(f"{pad}-\n{yaml_dump(v, indent + 1)}" if isinstance(v, (dict, list)) and v
                         else f"{pad}- {yaml_scalar(v) if not isinstance(v, (dict, list)) else ('{}' if isinstance(v, dict) else '[]')}"
                         for v in obj)
    return pad + yaml_scalar(obj)


def markdown(fr: dict, sha: str) -> str:
    f = lambda v: "–" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))
    rows = []
    for it in fr["held_out"]:
        p, c, m = it["prediction"], it["prediction"]["combination"], it["prediction"]["modes"]
        lo, hi = p["D_interval"]
        rows.append(f"| {it['id']} | {c['N']}/{c['M']} | {f(c['c'])} | {c['gamma']} | {c['ell']} | {c['amplitude']} | {c['sigma']} | "
                    f"n{c['inputs'][0]}/n{c['inputs'][1]} | {c['readout']}{' n' + str(c['readout_node']) if c['readout'] == 'node' else ''} | "
                    f"{f(m['mu_D'])} | {m['mu_I']:.3f} | {f(lo) if lo == hi else f'[{f(lo)}, {f(hi)}]'} |")
    return f"""# M9: eingefrorene Vorhersagen (Narrativ-Zwilling)

Trilayer nach Feldtheorie `AGENTS.md`:

| Schicht | Datei | Rolle |
|---|---|---|
| JSON | `m9_frozen_predictions.json` | maßgebliche, hash-geschützte Fassung |
| YAML | `m9_frozen_predictions.yaml` | inhaltsgleicher Strukturzwilling |
| Markdown | diese Datei | Erzählung |

Die beiden Zwillinge sind aus dem JSON erzeugt (`tools/make_trilayer_twins.py`). Ein Test prüft die Gleichheit.

**Kenndaten der Fassung:**
- SHA-256 des JSON (LF-normiert): `{sha}`
- eingefroren auf Stand `{fr['git_head_at_freeze'][:10]}`, vor jeder Kernrechnung an diesen Kombinationen
- `kernel_evaluated_before_freeze: {str(fr['kernel_evaluated_before_freeze']).lower()}`

**Begleitdokumente:**
- Herleitung: [`../docs/M9_HERLEITUNG.md`](../docs/M9_HERLEITUNG.md), dazu das Erratum [`../docs/M9_ERRATUM_1.md`](../docs/M9_ERRATUM_1.md)
- Prüfung und Ergebnis: [`../ROADMAP.md`](../ROADMAP.md), Abschnitte M9b und M9c
- Prüfregeln: das Feld `rules`

**Die Vorhersagen** (D = letzte Pause d ∈ 0…64 mit idealer Trefferquote ≥ p\\* = {fr['rules']['p_star']}; „–“ = bei keiner Pause):

| id | N/M | c | γ | ℓ | a | σ | Eingänge | H | μ_D | μ_I | D |
|---|---|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


def m10_markdown(p: dict, sha: str) -> str:
    c = p["conditions"]
    rows = "\n".join(f"| {k} | " + ("–" if v is None else f"{v['X']} / {v['Y']} | {v['amplitude']}") + (" | –" if v is None else "") + " |"
                     for k, v in c.items())
    cf = p["confirmatory"]
    return f"""# M10-Protokoll „Erinnerung unter Ablenkung“ (Narrativ-Zwilling)

Trilayer nach Feldtheorie `AGENTS.md`:

| Schicht | Datei | Rolle |
|---|---|---|
| JSON | `m10_protokoll.json` | maßgebliche Fassung |
| YAML | `m10_protokoll.yaml` | inhaltsgleicher Strukturzwilling |
| Markdown | diese Datei | Erzählung |

Die beiden Zwillinge sind aus dem JSON erzeugt (`tools/make_trilayer_twins.py`).

- **Status:** {p['status']}
- **SHA-256 des JSON** (LF-normiert): `{sha}`

Plan und Begründungen: [`../docs/M10_PLAN_ABLENKUNG.md`](../docs/M10_PLAN_ABLENKUNG.md) (Fassung 2).

**Netze:**
- modular: M = 3, c = 1/4;
- uniform: M = 1;
- beide mit N = 12, γ = 0,8, ℓ = 0,5, Zielknoten 0/4, a = 0,6, ohne Hebb;
- lineare Zwillinge zur Prüfung von A2/A3.

**Ablauf:**
- Zielreiz, Ruhe, dann ein Ablenkfenster W = 3 direkt vor der Ablesung (p = 0,5 je Schritt, X/Y je ½), danach Ablesung x_(d+1) mit σ = 0,02;
- Pausen d ∈ {{3, 4, 6}}, primär d = 4.

| Bedingung | Orte X / Y | Amplitude |
|---|---|---|
{rows}

**Ebene B** (Bayes, explizite Mischungs-Likelihood über 27 Fenstermuster):
- n_MC = {p['level_B']['n_mc']:,} Ziehungen je Schätzung, Blöcke zu {p['level_B']['block']:,}, eigener Strom je Schätzung;
- Aufgabe „letzter Kanal“: bedingt auf ≥ 1 Puls, Klassen X/Y gleich wahrscheinlich, K0 = N/A.

**Ebene D** (trainierte Decoder, **nur beschreibend**):
- {len(p['level_D']['seeds'])} Seeds, je {p['level_D']['n_train_per_class']} Trainings- und {p['level_D']['n_test_per_class']} Testepisoden je Klasse;
- Nearest-Mean und LDA (Ledoit-Wolf).

**Bestätigend:**
- {', '.join(cf['family'])} auf Ebene B bei d = {cf['delay']};
- einseitig, δ = {cf['delta']}, Holm α = {cf['holm']['alpha']};
- Z aus Monte-Carlo-Standardfehlern, SE = 0-Regel wie im JSON.

**Diagnosen:**
- A1 (Zustandsidentität) und A2 strukturell sind deterministisch.
- A2/A3 numerisch sind **statistische Alarme** (4 SE), keine sicheren Programmfehler; es gibt keine Wiederholung bis zum Bestehen.

**Ausschluss, Ressourcen, Smoke- und Entwicklungseinstellungen:** siehe JSON.
"""


def main() -> int:
    raw = SRC.read_bytes().replace(b"\r\n", b"\n")
    sha = hashlib.sha256(raw).hexdigest()
    fr = json.loads(raw.decode("utf-8"))
    (PROTOCOL / "m9_frozen_predictions.yaml").write_text(
        "# YAML twin of m9_frozen_predictions.json (generated; the JSON is authoritative)\n" + yaml_dump(fr) + "\n",
        encoding="utf-8", newline="\n")
    (PROTOCOL / "m9_frozen_predictions.md").write_text(markdown(fr, sha), encoding="utf-8", newline="\n")
    m10 = PROTOCOL / "m10_protokoll.json"
    raw10 = m10.read_bytes().replace(b"\r\n", b"\n")
    sha10 = hashlib.sha256(raw10).hexdigest()
    p10 = json.loads(raw10.decode("utf-8"))
    (PROTOCOL / "m10_protokoll.yaml").write_text(
        "# YAML twin of m10_protokoll.json (generated; the JSON is authoritative)\n" + yaml_dump(p10) + "\n",
        encoding="utf-8", newline="\n")
    (PROTOCOL / "m10_protokoll.md").write_text(m10_markdown(p10, sha10), encoding="utf-8", newline="\n")
    print(json.dumps({"m9_json_sha256": sha, "m10_json_sha256": sha10,
                      "written": ["m9_frozen_predictions.yaml", "m9_frozen_predictions.md", "m10_protokoll.yaml", "m10_protokoll.md"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
