"""
Tests unitarios para los métodos de síntesis (TOPSIS, Nash, Euclídeo), Votación Borda y Vetos.
"""

import pytest
import numpy as np
from src.optimization.pareto_optimizer import run_pareto_optimization
from src.optimization.synthesis import (
    synthesize_midpoint,
    check_vetoes,
    solve_topsis,
    solve_nash_bargaining,
    solve_weighted_euclidean,
)
from src.optimization.robustness import analyze_midpoint_robustness
from src.simulation.policy_vector import PolicyVector

def test_synthesis_and_three_methods():
    """Verifica que synthesize_midpoint ejecute TOPSIS, Nash y Euclídeo correctamente."""
    opt_res = run_pareto_optimization(algorithm_name="nsga3", pop_size=40, n_gen=20, seed=42)
    synthesis = synthesize_midpoint(opt_res)

    assert "policy_vector" in synthesis
    assert "topsis_chosen_index" in synthesis
    assert "nash_chosen_index" in synthesis
    assert "euclidean_chosen_index" in synthesis
    assert synthesis["veto_passed"] is True
    assert synthesis["synthesized_metrics"]["terminal_gdp_pc"] > 0

def test_veto_enforcement():
    """Verifica que un vector con violación extrema de límites sea detectado por el sistema de vetos."""
    # Vector con 95% de estatización (viola veto capitalista de max 80%)
    extreme_collectivist = PolicyVector([0.95, 0.9, 0.9, 0.8, 0.8, 0.8, 0.8, 0.1, 0.1, 0.1])
    passed, violations = check_vetoes(extreme_collectivist)
    assert passed is False
    assert len(violations) > 0
    assert any("VETO [Capitalista]" in v for v in violations)

def test_robustness_sensitivity_analysis():
    """Verifica que el análisis de sensibilidad monte-carlo sobre los pesos funcione correctamente."""
    opt_res = run_pareto_optimization(algorithm_name="nsga3", pop_size=40, n_gen=20, seed=42)
    rob = analyze_midpoint_robustness(
        pareto_F_natural=opt_res["pareto_F_natural"],
        pareto_X=opt_res["pareto_X"],
        n_perturbations=30,
        seed=42,
    )
    assert "topsis_stability_percentage" in rob
    assert 0.0 <= rob["topsis_stability_percentage"] <= 100.0
    assert len(rob["parameter_std_deviation"]) == 10
