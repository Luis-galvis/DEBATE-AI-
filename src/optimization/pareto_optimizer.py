"""
Optimizador Multiobjetivo con NSGA-III (pymoo) y Evaluación Vectorizada Rápida.
Calcula la Frontera de Pareto de 5 dimensiones sobre el espacio de políticas económicas [0.0, 1.0]^10.
"""

import time
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM

from src.simulation.policy_vector import PolicyVector
from src.simulation.solow_engine import MacroEconomy
from src.simulation.metrics import calculate_metrics

class EconomicPolicyOptimizationProblem(Problem):
    """
    Problema de optimización multiobjetivo:
    - 10 variables de decisión continuas en [0, 1].
    - 5 objetivos a MINIMIZAR:
      1. -PIB per cápita terminal (para maximizar)
      2. Gini promedio (para minimizar desigualdad)
      3. Máximo Deuda/PIB (para minimizar riesgo fiscal)
      4. -Resiliencia ante choques (para maximizar estabilidad)
      5. -Índice de Bienestar Social (para maximizar calidad de vida integral)
    """
    def __init__(self, calibration: Optional[Dict[str, Any]] = None, years: int = 30):
        super().__init__(
            n_var=10,
            n_obj=5,
            n_ieq_constr=0,
            xl=np.zeros(10),
            xu=np.ones(10),
        )
        self.calibration = calibration
        self.years = years

    def _evaluate(self, X: np.ndarray, out: Dict[str, Any], *args, **kwargs):
        n_candidates = X.shape[0]
        F = np.zeros((n_candidates, self.n_obj), dtype=np.float64)

        for i in range(n_candidates):
            policy = PolicyVector(X[i, :].tolist())
            econ = MacroEconomy(policy=policy, calibration=self.calibration, years=self.years)
            res_base = econ.simulate()
            m_base = calculate_metrics(res_base)

            # Objetivos a minimizar:
            f1_gdp = -float(m_base["terminal_gdp_pc"])                 # Maximizar PIB per cápita
            f2_gini = float(m_base["gini_avg"])                        # Minimizar Gini
            f3_debt = float(m_base["max_debt_gdp"]) / 100.0            # Minimizar Deuda/PIB
            f4_resilience = -float(m_base["resilience_score"])         # Maximizar Resiliencia
            f5_welfare = -float(m_base["social_welfare_index"])        # Maximizar Bienestar Social

            F[i, 0] = f1_gdp
            F[i, 1] = f2_gini
            F[i, 2] = f3_debt
            F[i, 3] = f4_resilience
            F[i, 4] = f5_welfare

        out["F"] = F

from data.data_loader import load_calibration_profile

def run_pareto_optimization(
    algorithm_name: str = "nsga3",
    pop_size: int = 40,
    n_gen: int = 25,
    seed: int = 42,
    random_seed: Optional[int] = None,
    calibration: Optional[Dict[str, Any]] = None,
    calibration_country: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ejecuta la optimización multiobjetivo con NSGA-III o NSGA-II.
    Mide el tiempo de evaluación y extrae la frontera de Pareto.
    """
    actual_seed = random_seed if random_seed is not None else seed
    
    calib_dict = calibration
    if calib_dict is None and calibration_country:
        calib_dict = load_calibration_profile(calibration_country.lower())

    problem = EconomicPolicyOptimizationProblem(calibration=calib_dict)
    t0 = time.time()

    if algorithm_name.lower() == "nsga3":
        ref_dirs = get_reference_directions("das-dennis", 5, n_partitions=3)
        actual_pop = max(pop_size, len(ref_dirs))
        algorithm = NSGA3(
            ref_dirs=ref_dirs,
            pop_size=actual_pop,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.9, eta=15),
            mutation=PM(prob=0.1, eta=20),
            eliminate_duplicates=True,
        )
    else:
        algorithm = NSGA2(
            pop_size=pop_size,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.9, eta=15),
            mutation=PM(prob=0.1, eta=20),
            eliminate_duplicates=True,
        )

    res = minimize(
        problem,
        algorithm,
        ("n_gen", n_gen),
        seed=actual_seed,
        verbose=False,
    )

    total_time = time.time() - t0
    n_evals = res.algorithm.evaluator.n_eval
    ms_per_eval = (total_time / max(1, n_evals)) * 1000.0

    pareto_X = np.atleast_2d(res.X) if res.X is not None else np.empty((0, 10))
    pareto_F = np.atleast_2d(res.F) if res.F is not None else np.empty((0, 5))

    # Magnitudes naturales
    natural_F = np.zeros_like(pareto_F)
    if natural_F.size > 0:
        natural_F[:, 0] = -pareto_F[:, 0]        # PIB pc
        natural_F[:, 1] = pareto_F[:, 1]         # Gini
        natural_F[:, 2] = pareto_F[:, 2] * 100.0 # Deuda %
        natural_F[:, 3] = -pareto_F[:, 3]        # Resiliencia
        natural_F[:, 4] = -pareto_F[:, 4]        # Bienestar

    return {
        "algorithm": algorithm_name.upper(),
        "total_time_seconds": round(total_time, 2),
        "total_evaluations": n_evals,
        "ms_per_evaluation": round(ms_per_eval, 3),
        "pareto_solutions_count": len(pareto_X),
        "pareto_X": pareto_X,
        "pareto_F_raw": pareto_F,
        "pareto_F_natural": natural_F,
        "X": pareto_X,
        "F": pareto_F,
        "objective_names": [
            "PIB per cápita terminal ($)",
            "Gini Promedio (0-1)",
            "Deuda Máxima / PIB (%)",
            "Índice de Resiliencia (0-100)",
            "Bienestar Social Integral (0-100)"
        ],
    }
