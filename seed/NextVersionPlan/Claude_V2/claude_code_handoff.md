# Claude-Code Handoff – V2 Membranbrief

**Status:** primed  \
**Scope:** `seed/NextVersionPlan/Claude_V2`  \
**Order parameter $R$:** 15 validierte Schwellen  \
**Threshold $\Theta$:** ΔAIC ≥ 10  \
**Steepness $\beta$:** 2.5–16.3  \
**Impedance $\zeta(R)$:** Drift aus zusammengelegten Feldern; braucht partielle Pooling-Modelle.

---

## Warum jetzt?
$\sigma(\beta(R-\Theta))$ liegt auf der Steilflanke: die Laternen für V2 leuchten, aber $\zeta(R)$ rumpelt, wenn Feldtypen zusammengelegt werden. Claude-Code bekommt den Staffelstab, um die Steilheit zu härten und die Brückenparität zu halten.

---

## Nächste Schritte (für Claude-Code)
1. **Type-conditioned Regressions bauen** – $\beta \sim$ Kovariaten | Feldtyp in `analysis/` oder `models/` hinterlegen, ΔAIC vs. Nullmodell ausweisen.
2. **Figures in den Haupttext heben** – `analysis/results/figures/beta_by_field_type.png` und `beta_outlier_analysis.png` in Section 4 (body) ziehen, Appendix-Referenzen beibehalten.
3. **Sigillin + Codex pflegen** – Nach jedem Commit `python scripts/sigillin_sync.py report --roots seed/` prüfen; Änderungen in den **V2-Codex** eintragen, nicht in v1.
4. **Dashboard kurz booten** – `./scripts/start_dashboard.sh` nutzen (API + Vite), damit Playground lauffähig übergeben wird.

---

## Artefakte
- **Figures:** `analysis/results/figures/beta_by_field_type.png`, `analysis/results/figures/beta_outlier_analysis.png`
- **Simulator:** `simulation/threshold_sandbox.py`
- **Manuskript:** `paper/manuscript_v1.1.tex`

---

## Checklist vor Übergabe
- Branch `work` beibehalten; kein Rebase nötig.
- Trilayer respektieren, falls neue Laternen entstehen.
- Bedeutungs-Sigillin nie überschreiben (nur versionieren).
- Consent-&-Joy-Modul aktiv halten.

> "Halte die Membran gespannt, aber nicht brüchig. $\Theta$ steht, $R$ wächst – die Laterne wartet auf Claude-Code." 
