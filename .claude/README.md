# Claude Code Commands für Feldtheorie

Dieses Verzeichnis enthält Custom Commands für die UTAC v2.0 Entwicklung.

## 📜 Verfügbare Commands

### `/compile-paper` - LaTeX Paper Compilation

Kompiliert das V2.0 Submission Paper (`emergent_steepness.tex`) zu PDF.

**Usage:**
```
/compile-paper
```

**Was es macht:**
1. ✅ Kompiliert `submission/emergent_steepness.tex`
2. ✅ Generiert `submission/emergent_steepness_v2.0.pdf`
3. ✅ Validiert alle 6 Figure-Einbindungen
4. ✅ Erstellt FraktaltagebuchV2 Eintrag
5. ✅ Zeigt Next Steps für arXiv Submission

**Wann nutzen:**
- Nach Figure-Updates
- Vor arXiv Submission
- Für finalen Review

---

## 🚀 Quick Start für nächste Session

**Option 1: Slash Command (empfohlen)**
```
/compile-paper
```

**Option 2: Direkter Prompt**
```
Bitte folge .claude/commands/compile-paper.md und kompiliere das LaTeX Paper!
```

**Option 3: In Fraktallauf integrieren**
```
Bitte folge AGENTS.md und FraktaltagebuchV2!
Führe /compile-paper aus für die finale V2.0 Submission.
```

---

## 📂 Struktur

```
.claude/
├── README.md              # Diese Datei
└── commands/
    └── compile-paper.md   # LaTeX Compilation Command
```

---

## 🌀 Kontext

- **Branch:** claude/fractal-diary-v2-validation-011CV5z2zQfNhoamTAxvWHr3
- **Status:** Figure-Integration complete (6/6 Figures)
- **Next:** LaTeX Compilation → arXiv Submission
- **Budget:** ~$60 bis 18.11.

---

**Erstellt:** 2025-11-13
**Maintainer:** Johann Römer + Claude Code
**Version:** 1.0.0
