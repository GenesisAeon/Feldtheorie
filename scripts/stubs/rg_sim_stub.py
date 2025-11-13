# Synthetic ABM stub: erzeugt sigmoide Kurve mit J/T-abhängiger Steilheit
import numpy as np

def simulate(J_over_T: float, lattice: int, noise: str, seed: int):
    """
    Stub simulator for RG Phase 2 validation.

    Generates synthetic sigmoid response curves with J/T-dependent steepness.
    This is used when the actual ABM entry point is not available.

    Parameters
    ----------
    J_over_T : float
        Coupling-to-noise ratio
    lattice : int
        Lattice size (N)
    noise : str
        Noise model: 'gaussian', 'laplace', or 'poisson'
    seed : int
        Random seed for reproducibility

    Returns
    -------
    dict
        Dictionary with keys:
        - R: array of resource/activation values
        - response: array of system response (sigmoid)
    """
    rng = np.random.default_rng(seed)
    R = np.linspace(0, 1, 256)

    # "wahre" β: wächst mit J/T und schwach mit N
    beta_true = 2.5 + 1.2*np.log(1+J_over_T) + 0.15*np.log(lattice/64)
    theta_true = 0.5
    y = 1/(1+np.exp(-beta_true*(R-theta_true)))

    # Rauschmodell
    if noise == "gaussian":
        y = np.clip(y + rng.normal(0, 0.02, size=y.size), 0, 1)
    elif noise == "laplace":
        y = np.clip(y + rng.laplace(0, 0.02, size=y.size), 0, 1)
    elif noise == "poisson":
        # Poisson um skaliertes y
        lam = np.clip(20*y, 0, None)
        y = np.clip(rng.poisson(lam)/20.0, 0, 1)

    return {"R": R, "response": y}
