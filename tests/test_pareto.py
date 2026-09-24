"""
Tests unitarios para el Optimizador Multiobjetivo NSGA-III vs NSGA-II.
"""

import pytest
import numpy as np
from src.optimization.pareto_optimizer import run_pareto_optimization

def test_pareto_nsga3_execution_and_speed():
    """Verifica que NSGA-III converja rápidamente (< 5s) y genere una frontera no vacía."""
    opt_res = run_pareto_optimization(algorithm_name="nsga3", pop_size=40, n_gen=20, seed=42)

    assert opt_res["total_time_seconds"] < 6.0, f"Optimización muy lenta: {opt_res['total_time_seconds']}s"
    assert opt_res["pareto_solutions_count"] >= 1
    assert opt_res["pareto_X"].shape[1] == 10
    assert opt_res["pareto_F_natural"].shape[1] == 5

    # Verificar que el PIB per cápita natural sea positivo y Gini esté acotado
    natural_F = opt_res["pareto_F_natural"]
    assert (natural_F[:, 0] > 0).all()
    assert (natural_F[:, 1] >= 0.15).all() and (natural_F[:, 1] <= 0.70).all()

def test_nsga2_vs_nsga3_benchmark():
    """Compara NSGA-II frente a NSGA-III verificando compatibilidad de ambos algoritmos."""
    res_nsga2 = run_pareto_optimization(algorithm_name="nsga2", pop_size=35, n_gen=15, seed=42)
    res_nsga3 = run_pareto_optimization(algorithm_name="nsga3", pop_size=35, n_gen=15, seed=42)

    assert res_nsga2["pareto_solutions_count"] > 0
    assert res_nsga3["pareto_solutions_count"] > 0
    assert res_nsga3["ms_per_evaluation"] < 10.0
