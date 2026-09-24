"""
Algoritmos de Síntesis de Políticas, Votación Borda, Gestión de Vetos y Robustez de Punto Medio.
Calcula la solución de compromiso mediante TOPSIS, Nash Bargaining, Kalai-Smorodinsky, Knee Point y Distancia Euclídea.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from src.simulation.policy_vector import (
    PolicyVector,
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)
from src.simulation.solow_engine import MacroEconomy
from src.simulation.metrics import calculate_metrics

def evaluate_agent_utilities(policy: PolicyVector) -> Dict[str, float]:
    """
    Calcula las utilidades subjetivas normalizadas [0, 100] de cada debatiente sobre un vector.
    """
    econ = MacroEconomy(policy=policy, years=30)
    res = econ.simulate()
    m = calculate_metrics(res)

    norm_gdp = np.clip(m["terminal_gdp_pc"] / 2.5, 0.0, 100.0)
    norm_equality = np.clip((1.0 - m["gini_avg"]) * 150.0, 0.0, 100.0)
    norm_freedom = np.clip(m["economic_freedom_avg"] * 10.0, 0.0, 100.0)
    norm_fiscal = float(m["fiscal_sustainability_score"])
    norm_resilience = float(m["resilience_score"])

    # 1. Utilidad Capitalista: Crecimiento (40%) + Libertad económica (35%) + Disciplina fiscal (25%)
    u_cap = 0.40 * norm_gdp + 0.35 * norm_freedom + 0.25 * norm_fiscal

    # 2. Utilidad Colectivista: Igualdad (50%) + Cobertura / Resiliencia (30%) + Propiedad social (20%)
    u_col = 0.50 * norm_equality + 0.30 * norm_resilience + 0.20 * (policy.real_state_share * 100.0)

    # 3. Utilidad Socialdemócrata: Bienestar nórdico equilibrado
    u_soc = 0.30 * norm_gdp + 0.30 * norm_equality + 0.20 * norm_fiscal + 0.20 * norm_resilience

    return {
        "capitalist_utility": round(float(u_cap), 2),
        "collectivist_utility": round(float(u_col), 2),
        "socdem_utility": round(float(u_soc), 2),
        "metrics": m,
    }

def get_utopia_and_nadir(pareto_F_natural: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcula los vectores de Utopía y Nadir empíricos a partir de la frontera de Pareto.
    Columnas: [PIB pc (max), Gini (min), Deuda % (min), Resiliencia (max), Bienestar (max)]
    """
    utopia = np.zeros(5)
    nadir = np.zeros(5)

    utopia[0] = np.max(pareto_F_natural[:, 0])
    nadir[0] = np.min(pareto_F_natural[:, 0])

    utopia[1] = np.min(pareto_F_natural[:, 1])
    nadir[1] = np.max(pareto_F_natural[:, 1])

    utopia[2] = np.min(pareto_F_natural[:, 2])
    nadir[2] = np.max(pareto_F_natural[:, 2])

    utopia[3] = np.max(pareto_F_natural[:, 3])
    nadir[3] = np.min(pareto_F_natural[:, 3])

    utopia[4] = np.max(pareto_F_natural[:, 4])
    nadir[4] = np.min(pareto_F_natural[:, 4])

    return utopia, nadir

def solve_topsis(
    pareto_F_natural: np.ndarray,
    weights: Optional[np.ndarray] = None,
) -> Tuple[int, np.ndarray]:
    """
    Aplica el método TOPSIS sobre la matriz de objetivos de la frontera de Pareto.
    """
    w = weights if weights is not None else np.array([0.25, 0.25, 0.15, 0.15, 0.20], dtype=np.float64)
    w = w / np.sum(w)
    m, n = pareto_F_natural.shape

    norm_matrix = np.zeros_like(pareto_F_natural, dtype=np.float64)
    for j in range(n):
        col_min = np.min(pareto_F_natural[:, j])
        col_max = np.max(pareto_F_natural[:, j])
        denom = max(1e-6, col_max - col_min)
        if j in (0, 3, 4):  # Maximizar
            norm_matrix[:, j] = (pareto_F_natural[:, j] - col_min) / denom
        else:  # Minimizar
            norm_matrix[:, j] = (col_max - pareto_F_natural[:, j]) / denom

    weighted = norm_matrix * w
    ideal = np.ones(n) * w
    anti_ideal = np.zeros(n)

    d_plus = np.sqrt(np.sum((weighted - ideal) ** 2, axis=1))
    d_minus = np.sqrt(np.sum((weighted - anti_ideal) ** 2, axis=1))

    closeness = d_minus / np.maximum(1e-6, d_plus + d_minus)
    best_idx = int(np.argmax(closeness))
    return best_idx, closeness

def solve_nash_bargaining(
    pareto_X: np.ndarray,
    disagreement_points: Optional[Dict[str, float]] = None,
) -> Tuple[int, np.ndarray]:
    """
    Encuentra la Solución de Negociación de Nash (NBS) que maximiza el producto de excedentes de utilidad.
    """
    d_points = disagreement_points or {"cap": 25.0, "col": 25.0, "soc": 30.0}
    n = len(pareto_X)
    nash_products = np.zeros(n, dtype=np.float64)

    for i in range(n):
        policy = PolicyVector(pareto_X[i, :].tolist())
        u = evaluate_agent_utilities(policy)

        surplus_cap = max(0.1, u["capitalist_utility"] - d_points["cap"])
        surplus_col = max(0.1, u["collectivist_utility"] - d_points["col"])
        surplus_soc = max(0.1, u["socdem_utility"] - d_points["soc"])

        nash_products[i] = surplus_cap * surplus_col * surplus_soc

    best_idx = int(np.argmax(nash_products))
    return best_idx, nash_products

def solve_kalai_smorodinsky(
    pareto_X: np.ndarray,
    disagreement_points: Optional[Dict[str, float]] = None,
) -> Tuple[int, np.ndarray]:
    """
    Solución de Negociación Kalai-Smorodinsky (KSBS):
    Mantiene la proporcionalidad de ganancias de utilidad respecto al vector de utopía.
    """
    d_points = disagreement_points or {"cap": 25.0, "col": 25.0, "soc": 30.0}
    d_vec = np.array([d_points["cap"], d_points["col"], d_points["soc"]], dtype=np.float64)
    
    n = len(pareto_X)
    utilities = np.zeros((n, 3), dtype=np.float64)
    for i in range(n):
        policy = PolicyVector(pareto_X[i, :].tolist())
        u = evaluate_agent_utilities(policy)
        utilities[i, 0] = u["capitalist_utility"]
        utilities[i, 1] = u["collectivist_utility"]
        utilities[i, 2] = u["socdem_utility"]

    # Vector ideal de utilidades (Utopia)
    u_max = np.max(utilities, axis=0)
    ideal_surplus = np.maximum(1.0, u_max - d_vec)

    # Buscar la solución que minimice la desviación angular del rayo (U_max - D)
    ks_scores = np.zeros(n, dtype=np.float64)
    for i in range(n):
        surplus = np.maximum(0.1, utilities[i, :] - d_vec)
        # Normalizar excedentes por el ideal
        norm_ratios = surplus / ideal_surplus
        # Kalai-Smorodinsky busca igualar las proporciones de ganancia (min-max ratio)
        ks_scores[i] = np.min(norm_ratios) / np.maximum(1e-4, np.max(norm_ratios))

    best_idx = int(np.argmax(ks_scores))
    return best_idx, ks_scores

def solve_knee_point(pareto_F_natural: np.ndarray) -> Tuple[int, np.ndarray]:
    """
    Identifica el punto 'Knee' (de máxima curvatura y mejor tasa de compromiso marginal).
    """
    m, n = pareto_F_natural.shape
    norm_matrix = np.zeros_like(pareto_F_natural, dtype=np.float64)
    for j in range(n):
        col_min = np.min(pareto_F_natural[:, j])
        col_max = np.max(pareto_F_natural[:, j])
        denom = max(1e-6, col_max - col_min)
        if j in (0, 3, 4):
            norm_matrix[:, j] = (pareto_F_natural[:, j] - col_min) / denom
        else:
            norm_matrix[:, j] = (col_max - pareto_F_natural[:, j]) / denom

    # Distancia al hiperplano que conecta extremos
    hyperplane_dists = np.sum(norm_matrix, axis=1) / np.sqrt(n)
    best_idx = int(np.argmax(hyperplane_dists))
    return best_idx, hyperplane_dists

def solve_weighted_euclidean(
    pareto_F_natural: np.ndarray,
    weights: Optional[np.ndarray] = None,
) -> Tuple[int, np.ndarray]:
    """
    Minimiza la distancia euclídea normalizada ponderada al punto utópico ideal.
    """
    w = weights if weights is not None else np.array([0.25, 0.25, 0.15, 0.15, 0.20], dtype=np.float64)
    w = w / np.sum(w)
    m, n = pareto_F_natural.shape

    dist_matrix = np.zeros_like(pareto_F_natural, dtype=np.float64)
    for j in range(n):
        col_min = np.min(pareto_F_natural[:, j])
        col_max = np.max(pareto_F_natural[:, j])
        denom = max(1e-6, col_max - col_min)
        if j in (0, 3, 4):
            dist_matrix[:, j] = (col_max - pareto_F_natural[:, j]) / denom
        else:
            dist_matrix[:, j] = (pareto_F_natural[:, j] - col_min) / denom

    weighted_dist = np.sqrt(np.sum(w * (dist_matrix ** 2), axis=1))
    best_idx = int(np.argmin(weighted_dist))
    return best_idx, weighted_dist

def check_vetoes(policy: PolicyVector, veto_rules: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, List[str]]:
    """
    Evalúa si un vector de políticas viola las líneas rojas declaradas por los debatientes.
    """
    rules = veto_rules or [
        {"dim": "state_ownership", "min": 0.0, "max": 0.80, "agent": "Capitalista", "reason": "Estatización superior al 80% destruye incentivos"},
        {"dim": "trade_openness", "min": 0.30, "max": 1.0, "agent": "Capitalista", "reason": "Autarquía comercial asfixia el crecimiento"},
        {"dim": "social_transfers_coverage", "min": 0.25, "max": 1.0, "agent": "Colectivista", "reason": "Desprotección social extrema es inaceptable"},
        {"dim": "central_bank_independence", "min": 0.40, "max": 1.0, "agent": "Socialdemócrata", "reason": "Subordinación inflacionaria del Banco Central"},
        {"dim": "fiscal_rule_strictness", "min": 0.30, "max": 1.0, "agent": "Socialdemócrata", "reason": "Ausencia de ancla fiscal genera insolvencia"},
    ]

    p_dict = policy.to_dict()
    violations = []
    for rule in rules:
        val = p_dict[rule["dim"]]
        if val < rule["min"] or val > rule["max"]:
            violations.append(
                f"VETO [{rule['agent']}]: Parámetro '{rule['dim']}'={val:.2f} fuera de límite [{rule['min']}, {rule['max']}]. Razón: {rule['reason']}"
            )

    return (len(violations) == 0), violations

def synthesize_midpoint(
    pareto_results: Dict[str, Any],
    veto_rules: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Aplica los 5 métodos (TOPSIS, Nash, Kalai-Smorodinsky, Knee Point, Euclídeo),
    verifica vetos y ejecuta votación Borda.
    """
    pareto_X = pareto_results["pareto_X"]
    pareto_F_nat = pareto_results["pareto_F_natural"]

    utopia, nadir = get_utopia_and_nadir(pareto_F_nat)

    # 1. Ejecución de los métodos
    idx_topsis, scores_topsis = solve_topsis(pareto_F_nat)
    idx_nash, scores_nash = solve_nash_bargaining(pareto_X)
    idx_ks, scores_ks = solve_kalai_smorodinsky(pareto_X)
    idx_knee, scores_knee = solve_knee_point(pareto_F_nat)
    idx_euclid, scores_euclid = solve_weighted_euclidean(pareto_F_nat)

    candidate_indices = [idx_topsis, idx_nash, idx_ks, idx_knee, idx_euclid]

    # 2. Votación Borda sobre los candidatos
    n = len(pareto_X)
    borda_scores = np.zeros(n, dtype=np.float64)
    borda_scores += np.argsort(np.argsort(scores_topsis))
    borda_scores += np.argsort(np.argsort(scores_nash))
    borda_scores += np.argsort(np.argsort(scores_ks))
    borda_scores += np.argsort(np.argsort(scores_knee))
    borda_scores += np.argsort(np.argsort(-scores_euclid))

    # 3. Filtrar por vetos
    valid_candidates = []
    for idx in np.argsort(-borda_scores):
        vec = PolicyVector(pareto_X[idx, :].tolist())
        passed, _ = check_vetoes(vec, veto_rules)
        if passed:
            valid_candidates.append(idx)

    final_idx = valid_candidates[0] if valid_candidates else int(np.argmax(borda_scores))
    final_vector = PolicyVector(pareto_X[final_idx, :].tolist())
    passed_veto, active_vetos = check_vetoes(final_vector, veto_rules)

    unique_chosen = len(set(candidate_indices))
    method_divergence = (unique_chosen > 2)

    agent_eval = evaluate_agent_utilities(final_vector)

    return {
        "selected_index": final_idx,
        "policy_vector": final_vector,
        "vector_values": final_vector.to_dict(),
        "utopia_point": utopia.round(2).tolist(),
        "nadir_point": nadir.round(2).tolist(),
        "topsis_chosen_index": idx_topsis,
        "nash_chosen_index": idx_nash,
        "kalai_smorodinsky_chosen_index": idx_ks,
        "knee_point_chosen_index": idx_knee,
        "euclidean_chosen_index": idx_euclid,
        "method_agreement": not method_divergence,
        "methods_summary": {
            "TOPSIS": {"index": idx_topsis, "objectives": pareto_F_nat[idx_topsis].tolist()},
            "Nash": {"index": idx_nash, "objectives": pareto_F_nat[idx_nash].tolist()},
            "KalaiSmorodinsky": {"index": idx_ks, "objectives": pareto_F_nat[idx_ks].tolist()},
            "KneePoint": {"index": idx_knee, "objectives": pareto_F_nat[idx_knee].tolist()},
            "Euclidean": {"index": idx_euclid, "objectives": pareto_F_nat[idx_euclid].tolist()},
        },
        "veto_passed": passed_veto,
        "active_vetos": active_vetos,
        "agent_utilities": agent_eval,
        "synthesized_metrics": agent_eval["metrics"],
    }
