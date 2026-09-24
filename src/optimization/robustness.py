"""
Análisis de Sensibilidad y Robustez del Punto Medio de Síntesis.
Evalúa la estabilidad del compromiso frente a variaciones de ponderación (±20%) y esquemas de normalización.
"""

from typing import Dict, Any, List
import numpy as np
from src.optimization.synthesis import solve_topsis, solve_weighted_euclidean

def analyze_midpoint_robustness(
    pareto_F_natural: np.ndarray,
    pareto_X: np.ndarray,
    n_perturbations: int = 60,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Realiza un análisis de sensibilidad monte-carlo sobre las ponderaciones de los objetivos.
    """
    rng = np.random.default_rng(seed)
    base_weights = np.array([0.25, 0.25, 0.15, 0.15, 0.20], dtype=np.float64)

    selected_indices_topsis = []
    selected_indices_euclid = []

    for _ in range(n_perturbations):
        # Perturbar ponderaciones ±20%
        noise = rng.uniform(0.80, 1.20, size=5)
        w_perturbed = base_weights * noise
        w_perturbed = w_perturbed / np.sum(w_perturbed)

        idx_t, _ = solve_topsis(pareto_F_natural, weights=w_perturbed)
        idx_e, _ = solve_weighted_euclidean(pareto_F_natural, weights=w_perturbed)

        selected_indices_topsis.append(idx_t)
        selected_indices_euclid.append(idx_e)

    # Identificar frecuencias de soluciones seleccionadas
    unique_t, counts_t = np.unique(selected_indices_topsis, return_counts=True)
    modal_topsis_idx = int(unique_t[np.argmax(counts_t)])
    topsis_stability_pct = float(np.max(counts_t) / n_perturbations * 100.0)

    unique_e, counts_e = np.unique(selected_indices_euclid, return_counts=True)
    modal_euclid_idx = int(unique_e[np.argmax(counts_e)])
    euclid_stability_pct = float(np.max(counts_e) / n_perturbations * 100.0)

    # Dispersión en el espacio de parámetros de las soluciones seleccionadas
    chosen_vectors_t = pareto_X[selected_indices_topsis, :]
    param_stds = np.std(chosen_vectors_t, axis=0).round(3).tolist()

    return {
        "n_perturbations": n_perturbations,
        "topsis_modal_index": modal_topsis_idx,
        "topsis_stability_percentage": round(topsis_stability_pct, 1),
        "euclid_modal_index": modal_euclid_idx,
        "euclid_stability_percentage": round(euclid_stability_pct, 1),
        "parameter_std_deviation": param_stds,
        "is_highly_robust": bool(topsis_stability_pct >= 60.0),
        "summary": (
            f"El punto medio presenta una estabilidad del {topsis_stability_pct:.1f}% bajo perturbaciones de pesos (±20%). "
            f"La dispersión promedio en parámetros es de {np.mean(param_stds):.3f}."
        ),
    }
