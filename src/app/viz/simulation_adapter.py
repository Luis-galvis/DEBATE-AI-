"""
Adaptador de Simulación Macroeconómica: Ejecuta y formatea trayectorias a 30 años,
bandas estocásticas Monte Carlo (p10-p50-p90), resiliencia ante los 7 choques y matrices comparativas.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.simulation.policy_vector import (
    PolicyVector,
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)
from src.simulation.solow_engine import MacroEconomy
from src.simulation.shocks import ALL_SCENARIOS, get_scenario_shocks
from src.simulation.metrics import calculate_metrics
from src.simulation.monte_carlo import run_monte_carlo
from src.app.viz.metrics_catalog import METRICS_CATALOG, COLOR_PALETTE, SYSTEM_LABELS

def get_archetype_and_consensus_vectors(session_data: Optional[Dict[str, Any]] = None) -> Dict[str, PolicyVector]:
    """Obtiene los 4 vectores de política (3 arquetipos + consenso final sintetizado)."""
    vectors = {
        "capitalist": CAPITALIST_INITIAL_VECTOR,
        "collectivist": COLLECTIVIST_INITIAL_VECTOR,
        "socdem": SOCDEM_INITIAL_VECTOR,
    }
    
    # Obtener consenso si existe en la sesión
    if session_data and "synthesis" in session_data and session_data["synthesis"]:
        c_dict = session_data["synthesis"].get("consensus_vector", {})
        if c_dict and len(c_dict) == 10:
            vectors["consensus"] = PolicyVector(**c_dict)
            return vectors
            
    # Fallback predeterminado si aún no hay consenso sintetizado
    vectors["consensus"] = PolicyVector(
        state_ownership=0.25,
        max_tax_rate=0.48,
        tax_progressivity=0.65,
        public_spending_gdp=0.42,
        social_transfers_coverage=0.60,
        market_regulation=0.45,
        labor_protection=0.55,
        trade_openness=0.75,
        fiscal_rule_strictness=0.70,
        central_bank_independence=0.85,
    )
    return vectors

from data.data_loader import load_calibration_profile

def run_multi_position_simulations(
    vectors: Dict[str, PolicyVector],
    calibration_country: str = "Colombia",
    scenario: str = "baseline"
) -> Dict[str, Dict[str, np.ndarray]]:
    """Ejecuta la simulación macroeconómica continua para las 4 posiciones en un escenario dado."""
    results = {}
    calib = load_calibration_profile(calibration_country.lower())
    shocks = get_scenario_shocks(scenario, years=30)
    for pos_id, p_vec in vectors.items():
        eco = MacroEconomy(
            policy=p_vec,
            calibration=calib,
            years=30,
        )
        sim_res = eco.simulate(shock_series=shocks)
        results[pos_id] = sim_res
    return results

def compute_all_metrics_table(
    sim_results: Dict[str, Dict[str, np.ndarray]]
) -> pd.DataFrame:
    """Calcula el catálogo completo de métricas para las 4 posiciones y las formatea en un DataFrame."""
    metrics_by_pos = {}
    for pos_id, res in sim_results.items():
        base_m = calculate_metrics(res)
        
        # Enriquecer con métricas de quintiles y trabajo
        gdp = res["gdp"]
        gdp_pc = res["gdp_per_capita"]
        q_inc = res.get("quintile_disposable_income", np.zeros((30, 5)))
        total_q = np.sum(q_inc, axis=1) + 1e-9
        q1_share = float(np.mean(q_inc[:, 0] / total_q) * 100.0)
        q5_share = float(np.mean(q_inc[:, 4] / total_q) * 100.0)
        
        # Salario real y productividad
        prod = float(np.mean(res.get("productivity", gdp_pc * 1.2)))
        labor_sh = float(np.mean(res.get("labor_share", np.full(30, 52.0))))
        real_w = float(np.mean(res.get("real_wage", np.full(30, 100.0))))
        
        full_m = dict(base_m)
        full_m["labor_productivity"] = round(prod, 1)
        full_m["investment_gdp"] = round(float(np.mean(res.get("investment", gdp * 0.22) / gdp * 100.0)), 1)
        full_m["q1_income_share"] = round(q1_share, 1)
        full_m["q5_income_share"] = round(q5_share, 1)
        full_m["labor_share"] = round(labor_sh, 1)
        full_m["real_wage_index"] = round(real_w, 1)
        
        metrics_by_pos[pos_id] = full_m
        
    rows = []
    for m_key, m_info in METRICS_CATALOG.items():
        row = {
            "metric_key": m_key,
            "name": m_info["name"],
            "category": m_info["category"],
            "unit": m_info["unit"],
            "direction": m_info["direction"],
            "better_is_higher": m_info["better_is_higher"],
        }
        for pos_id in ["capitalist", "collectivist", "socdem", "consensus"]:
            if pos_id in metrics_by_pos:
                row[pos_id] = metrics_by_pos[pos_id].get(m_key, np.nan)
        rows.append(row)
        
    return pd.DataFrame(rows)

def compute_normalized_radar_data(df_metrics: pd.DataFrame) -> pd.DataFrame:
    """Normaliza las métricas seleccionadas en [0, 100] orientadas a 'mayor es mejor' para radar charts."""
    radar_keys = [
        "terminal_gdp_pc",
        "gini_avg",
        "terminal_debt_gdp",
        "unemployment_avg",
        "resilience_score",
        "social_welfare_index",
        "life_expectancy_avg",
        "economic_freedom_avg"
    ]
    
    sub_df = df_metrics[df_metrics["metric_key"].isin(radar_keys)].copy()
    norm_rows = []
    
    for _, row in sub_df.iterrows():
        key = row["metric_key"]
        higher_better = row["better_is_higher"]
        vals = [row["capitalist"], row["collectivist"], row["socdem"], row["consensus"]]
        min_v = min(vals)
        max_v = max(vals)
        rng = max(1e-6, max_v - min_v)
        
        norm_row = {
            "metric_key": key,
            "name": row["name"],
        }
        for pos_id in ["capitalist", "collectivist", "socdem", "consensus"]:
            raw_v = row[pos_id]
            if higher_better:
                score = (raw_v - min_v) / rng * 80.0 + 20.0  # escala 20 a 100
            else:
                score = (max_v - raw_v) / rng * 80.0 + 20.0  # invertido
            norm_row[pos_id] = round(float(score), 1)
        norm_rows.append(norm_row)
        
    return pd.DataFrame(norm_rows)

def compute_shock_resilience_comparison(
    vectors: Dict[str, PolicyVector],
    calibration_country: str = "Colombia"
) -> pd.DataFrame:
    """Calcula la caída máxima (% drawdown) y tiempo de recuperación ante cada uno de los 7 choques."""
    records = []
    
    for sc_name in ALL_SCENARIOS:
        sims = run_multi_position_simulations(vectors, calibration_country, scenario=sc_name)
        for pos_id, res in sims.items():
            gdp = res["gdp"]
            gdp_diffs = np.diff(gdp) / gdp[:-1]
            max_drop = abs(min(0.0, float(np.min(gdp_diffs)))) * 100.0
            
            # Tiempo de recuperación (años hasta volver a la senda previa)
            min_idx = int(np.argmin(gdp_diffs)) + 1
            recovery_years = 1
            for t in range(min_idx, len(gdp)):
                if gdp[t] >= gdp[max(0, min_idx - 2)]:
                    recovery_years = t - min_idx + 1
                    break
            else:
                recovery_years = max(1, 30 - min_idx)
                
            records.append({
                "scenario": sc_name,
                "position": pos_id,
                "position_name": SYSTEM_LABELS.get(pos_id, pos_id),
                "max_drawdown_pct": round(max_drop, 2),
                "recovery_years": recovery_years,
            })
            
    return pd.DataFrame(records)

from src.simulation.monte_carlo import run_monte_carlo

def generate_monte_carlo_trajectories(
    policy_vector: PolicyVector,
    scenario_name: str = "baseline",
    n_runs: int = 200,
    seed: int = 42,
) -> Dict[str, Any]:
    """Genera bandas de percentiles p10, p50, p90 para trayectoria estocástica."""
    return run_monte_carlo(
        policy=policy_vector,
        scenario_name=scenario_name,
        runs=n_runs,
        seed=seed,
    )
