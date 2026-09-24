"""
Cálculo de Métricas Macroeconómicas, Sociales, Fiscales y de Resiliencia.
Evalúa las trayectorias temporales de la simulación y genera indicadores sintéticos.
"""

from typing import Dict, Any, List
import numpy as np

def calculate_metrics(results: Dict[str, np.ndarray]) -> Dict[str, float]:
    """
    Calcula el resumen de indicadores clave a partir de la trayectoria de simulación.
    """
    gdp = results["gdp"]
    gdp_pc = results["gdp_per_capita"]
    gini = results["gini_disposable"]
    poverty = results["poverty_rate"]
    debt_gdp = results["debt_to_gdp"]
    unemp = results["unemployment"]
    inf = results["inflation"]
    life_exp = results["life_expectancy"]
    econ_free = results["economic_freedom"]
    co2 = results["co2_emissions"]
    rd = results["rd_spending"]

    T = len(gdp)

    # 1. Crecimiento económico
    cagr_gdp = float(((gdp[-1] / max(1.0, gdp[0])) ** (1.0 / max(1, T - 1)) - 1.0) * 100.0)
    terminal_gdp_pc = float(gdp_pc[-1])

    # 2. Desigualdad y Pobreza
    avg_gini = float(np.mean(gini))
    terminal_gini = float(gini[-1])
    avg_poverty = float(np.mean(poverty) * 100.0)

    # 3. Sostenibilidad Fiscal y Deuda
    max_debt = float(np.max(debt_gdp) * 100.0)
    terminal_debt = float(debt_gdp[-1] * 100.0)
    # Penalización cuadrática si la deuda supera el 90%
    debt_penalty = max(0.0, (terminal_debt - 75.0) * 1.5)
    fiscal_sustainability = float(np.clip(100.0 - (terminal_debt * 0.5 + debt_penalty), 0.0, 100.0))

    # 4. Estabilidad Nominal, Mercado Laboral y Recaudo Tributario
    avg_unemployment = float(np.mean(unemp) * 100.0)
    terminal_unemployment = float(unemp[-1] * 100.0)
    avg_inflation = float(np.mean(inf) * 100.0)

    inf_series = results.get("informality_rate", np.full(T, 0.56))
    avg_informality = float(np.mean(inf_series) * 100.0)
    terminal_informality = float(inf_series[-1] * 100.0)

    # Recaudo tributario sobre el PIB
    tax_rev = results.get("tax_revenue", gdp * 0.20)
    tax_ratio = (tax_rev / np.maximum(1e-4, gdp)) * 100.0
    avg_tax_revenue_gdp = float(np.mean(tax_ratio))
    terminal_tax_revenue_gdp = float(tax_ratio[-1])

    # 5. Resiliencia ante Choques: caída máxima y volatilidad
    gdp_diffs = np.diff(gdp) / gdp[:-1]
    max_drawdown = float(abs(min(0.0, float(np.min(gdp_diffs)))) * 100.0)
    gdp_volatility = float(np.std(gdp_diffs) * 100.0)
    resilience_score = float(np.clip(100.0 - (max_drawdown * 3.5 + gdp_volatility * 4.0), 0.0, 100.0))

    # 6. Desarrollo Humano, Innovación y Medio Ambiente
    avg_life_expectancy = float(np.mean(life_exp))
    avg_economic_freedom = float(np.mean(econ_free))
    avg_rd_gdp = float(np.mean(rd) * 100.0)
    total_co2 = float(np.sum(co2))

    # 7. Índice Compuesto de Bienestar Social Integral (Social Welfare Index)
    # Pondera: Crecimiento (25%), Igualdad (25%), Salud/Vida (20%), Libertad (15%), Sostenibilidad Fiscal (15%)
    norm_gdp = np.clip(terminal_gdp_pc / 2.5, 0.0, 100.0)
    norm_equality = np.clip((1.0 - avg_gini) * 150.0, 0.0, 100.0)
    norm_life = np.clip((avg_life_expectancy - 60.0) * 4.0, 0.0, 100.0)
    norm_freedom = np.clip(avg_economic_freedom * 10.0, 0.0, 100.0)

    social_welfare = float(
        0.25 * norm_gdp
        + 0.25 * norm_equality
        + 0.20 * norm_life
        + 0.15 * norm_freedom
        + 0.15 * fiscal_sustainability
    )

    return {
        "gdp_growth_cagr": round(cagr_gdp, 2),
        "terminal_gdp_pc": round(terminal_gdp_pc, 2),
        "gini_avg": round(avg_gini, 3),
        "gini_terminal": round(terminal_gini, 3),
        "poverty_rate_avg": round(avg_poverty, 1),
        "max_debt_gdp": round(max_debt, 1),
        "terminal_debt_gdp": round(terminal_debt, 1),
        "fiscal_sustainability_score": round(fiscal_sustainability, 1),
        "unemployment_avg": round(avg_unemployment, 1),
        "unemployment_terminal": round(terminal_unemployment, 1),
        "informality_avg": round(avg_informality, 1),
        "informality_terminal": round(terminal_informality, 1),
        "tax_revenue_gdp_avg": round(avg_tax_revenue_gdp, 1),
        "tax_revenue_terminal": round(terminal_tax_revenue_gdp, 1),
        "inflation_avg": round(avg_inflation, 1),
        "max_drawdown": round(max_drawdown, 2),
        "resilience_score": round(resilience_score, 1),
        "life_expectancy_avg": round(avg_life_expectancy, 1),
        "economic_freedom_avg": round(avg_economic_freedom, 2),
        "rd_gdp_avg": round(avg_rd_gdp, 2),
        "total_co2": round(total_co2, 1),
        "social_welfare_index": round(social_welfare, 1),
    }

