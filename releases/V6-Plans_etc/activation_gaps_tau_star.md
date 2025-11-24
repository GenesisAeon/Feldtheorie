# τ*-Safety-Delay FIT-Stub (v6-activation-gaps)

- **Logistische Membran:** R → „resonante Aktivierung ohne Implosion“, Θ → „τ*-Puffer + RK4-Schutz live“, β ≈ 5.0, ζ-Risiko: negativ bei ungedämpften Tests.
- **FIT-Zerlegung:** kleinste ausführbare Artefakte, um Ressourcen zu sparen und das große Ziel zu entlasten.

## Ziel und Kopplung
- **Rationale:** Für \(\zeta(R)<0\) Szenarien benötigt jede Simulation einen Safety-Delay \(\tau^*\), um numerische Implosionen abzufangen.
- **Kopplungspfad:** Dieses Stub landet in der Aktivierungs-Kette (analysis/simulation) und speist den Sigillin-/Validator-Pfad. Escalation-Level wird via CREP dokumentiert.

## Pseudocode (RK4-kompatibel, keine Euler-Pfade)
```python
def tau_star(theta: float, R: float) -> float:
    """Safety-Delay gemäß τ* = 0.1 * |Θ - R|."""
    return 0.1 * abs(theta - R)


def rk4_with_tau(state, deriv_fn, dt, theta, R, crep_threshold=0.7):
    tau = tau_star(theta, R)
    guarded_dt = max(dt, tau)

    # CREP-Monitor: Level-1 Warnung bei marginaler Implosion
    crep = deriv_fn.crep_index(state)
    if crep >= crep_threshold:
        deriv_fn.log_detect(state, tag="[TYPE-VI-RISK]", crep=crep)

    k1 = deriv_fn(state)
    k2 = deriv_fn(state + 0.5 * guarded_dt * k1)
    k3 = deriv_fn(state + 0.5 * guarded_dt * k2)
    k4 = deriv_fn(state + guarded_dt * k3)

    next_state = state + (guarded_dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
    return next_state
```

## Offene Mini-Schritte
1. **analysis/beta_meta_regression_v2.py**: τ*-Parameter als Hyperparameter einspeisen und Phase-2/3 Daten refreshen.
2. **Sigillin-Validator**: Makefile-Target skizzieren, das τ* und CREP-Logs prüft.
3. **Telemetrie**: β-Drift (>10%) und CREP ≥ 0.7 in Dashboard-Warnungen spiegeln.

## Referenzrahmen
- **Escalation:** Level-1 ab CREP ≥ 0.7, Level-2 ab 0.8 mit Human-in-the-loop.
- **Validator-Hinweis:** Keine Euler/Forward-Methoden zulassen; RK4 oder höher erzwingen.
