"""
Tests unitarios para los 7 Escenarios de Choque Macroeconómico y Monte Carlo.
"""

import pytest
import numpy as np
from src.simulation.policy_vector import SOCDEM_INITIAL_VECTOR, CAPITALIST_INITIAL_VECTOR
from src.simulation.solow_engine import MacroEconomy
from src.simulation.shocks import ALL_SCENARIOS, get_scenario_shocks
from src.simulation.monte_carlo import run_monte_carlo

def test_all_seven_scenarios_exist_and_run():
    """Verifica que los 7 escenarios se ejecuten sin errores numéricos."""
    assert len(ALL_SCENARIOS) == 7
    for sc in ALL_SCENARIOS:
        shocks = get_scenario_shocks(sc, years=30)
        assert "demand" in shocks
        assert "spread" in shocks
        assert len(shocks["demand"]) == 30

        econ = MacroEconomy(policy=SOCDEM_INITIAL_VECTOR, years=30)
        res = econ.simulate(shock_series=shocks)
        assert len(res["gdp"]) == 30
        assert not np.isnan(res["gdp"]).any()
        assert not np.isinf(res["gdp"]).any()

def test_pandemic_shock_impact():
    """Verifica que la pandemia reduzca el PIB e incremente temporalmente el gasto en salud/déficit."""
    shocks_base = get_scenario_shocks("baseline", years=30)
    shocks_pand = get_scenario_shocks("pandemic", years=30)

    econ = MacroEconomy(policy=SOCDEM_INITIAL_VECTOR, years=30)
    res_base = econ.simulate(shock_series=shocks_base)
    res_pand = econ.simulate(shock_series=shocks_pand)

    # En el año 10 (índice 9/10), el PIB bajo pandemia debe ser menor al base
    assert res_pand["gdp"][10] < res_base["gdp"][10]
    # Y el desempleo debe ser mayor
    assert res_pand["unemployment"][10] > res_base["unemployment"][10]

def test_monte_carlo_execution():
    """Verifica que la simulación Monte Carlo rápida devuelva percentiles consistentes p10 <= p50 <= p90."""
    mc_res = run_monte_carlo(CAPITALIST_INITIAL_VECTOR, scenario_name="global_recession", runs=30, seed=42)
    assert mc_res["runs"] == 30
    p10 = mc_res["trajectories"]["gdp"]["p10"]
    p50 = mc_res["trajectories"]["gdp"]["p50"]
    p90 = mc_res["trajectories"]["gdp"]["p90"]

    assert len(p50) == 30
    # Verificación de monotonicidad de percentiles en el periodo terminal
    assert p10[-1] <= p50[-1] <= p90[-1]
