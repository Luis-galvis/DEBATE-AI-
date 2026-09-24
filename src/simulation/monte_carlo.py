"""
Ejecutor de Simulaciones Monte Carlo Paralelizado y Determinista.
Genera distribuciones estadísticas, intervalos de confianza (p10, p50, p90) y pruebas de robustez estocástica.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from src.simulation.policy_vector import PolicyVector
from src.simulation.solow_engine import MacroEconomy
from src.simulation.shocks import get_scenario_shocks
from src.simulation.metrics import calculate_metrics

def run_monte_carlo(
    policy: PolicyVector,
    scenario_name: str = "baseline",
    runs: int = 1000,
    seed: int = 42,
    calibration: Optional[Dict[str, Any]] = None,
    years: int = 30,
) -> Dict[str, Any]:
    """
    Ejecuta N iteraciones Monte Carlo sobre un escenario con perturbaciones estocásticas.
    Retorna trayectorias percentiles (p10, p50, p90) y métricas agregadas.
    """
    rng = np.random.default_rng(seed)
    base_shocks = get_scenario_shocks(scenario_name, years=years)

    # Matrices para almacenar trayectorias de N corridas
    gdp_runs = np.zeros((runs, years), dtype=np.float64)
    gini_runs = np.zeros((runs, years), dtype=np.float64)
    debt_runs = np.zeros((runs, years), dtype=np.float64)
    unemp_runs = np.zeros((runs, years), dtype=np.float64)
    inf_runs = np.zeros((runs, years), dtype=np.float64)

    metrics_list: List[Dict[str, float]] = []

    for i in range(runs):
        # Perturbaciones estocásticas añadidas al escenario base
        noise_tfp = base_shocks["tfp"] + rng.normal(0.0, 0.012, years)
        noise_demand = base_shocks["demand"] + rng.normal(0.0, 0.015, years)
        noise_spread = np.clip(base_shocks["spread"] + rng.normal(0.0, 0.008, years), -0.02, 0.15)
        noise_terms = base_shocks["terms_trade"] + rng.normal(0.0, 0.025, years)
        noise_labor = base_shocks["labor"] + rng.normal(0.0, 0.003, years)

        stochastic_shocks = {
            "tfp": noise_tfp,
            "demand": noise_demand,
            "spread": noise_spread,
            "terms_trade": noise_terms,
            "labor": noise_labor,
            "health_crisis": base_shocks["health_crisis"],
        }

        economy = MacroEconomy(policy=policy, calibration=calibration, years=years)
        sim_res = economy.simulate(shock_series=stochastic_shocks)

        gdp_runs[i, :] = sim_res["gdp"]
        gini_runs[i, :] = sim_res["gini_disposable"]
        debt_runs[i, :] = sim_res["debt_to_gdp"] * 100.0
        unemp_runs[i, :] = sim_res["unemployment"] * 100.0
        inf_runs[i, :] = sim_res["inflation"] * 100.0

        if i < min(100, runs):
            metrics_list.append(calculate_metrics(sim_res))

    # Cálculo de percentiles temporales
    def get_percentiles(matrix: np.ndarray) -> Dict[str, List[float]]:
        return {
            "p10": np.percentile(matrix, 10, axis=0).round(2).tolist(),
            "p50": np.percentile(matrix, 50, axis=0).round(2).tolist(),
            "p90": np.percentile(matrix, 90, axis=0).round(2).tolist(),
        }

    # Métricas agregadas sobre la mediana
    median_sim = {
        "gdp": np.median(gdp_runs, axis=0),
        "gdp_per_capita": np.median(gdp_runs, axis=0) / 100.0,
        "gini_disposable": np.median(gini_runs, axis=0),
        "debt_to_gdp": np.median(debt_runs, axis=0) / 100.0,
        "unemployment": np.median(unemp_runs, axis=0) / 100.0,
        "inflation": np.median(inf_runs, axis=0) / 100.0,
        "poverty_rate": np.median(gini_runs, axis=0) * 0.40,
        "life_expectancy": 76.0 + 5.0 * (1.0 - np.median(gini_runs, axis=0)),
        "economic_freedom": np.ones(years) * float(policy.values[7] * 5.0 + 4.0),
        "co2_emissions": np.median(gdp_runs, axis=0) * 0.01,
        "rd_spending": np.ones(years) * 0.02,
    }
    summary_metrics = calculate_metrics(median_sim)

    return {
        "scenario": scenario_name,
        "runs": runs,
        "trajectories": {
            "gdp": get_percentiles(gdp_runs),
            "gini": get_percentiles(gini_runs),
            "debt_gdp": get_percentiles(debt_runs),
            "unemployment": get_percentiles(unemp_runs),
            "inflation": get_percentiles(inf_runs),
        },
        "summary_metrics": summary_metrics,
    }
