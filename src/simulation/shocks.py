"""
Definición de los 7 Escenarios de Choque Macroeconómico para Pruebas de Estrés.
Garantiza que los tres sistemas debatan sobre las mismas perturbaciones exógenas.
"""

from typing import Dict, Any
import numpy as np

def get_scenario_shocks(scenario_name: str, years: int = 30) -> Dict[str, np.ndarray]:
    """
    Genera los vectores de choques exógenos para un escenario específico a lo largo de T años.
    """
    T = years
    tfp = np.zeros(T)
    demand = np.zeros(T)
    spread = np.zeros(T)
    labor = np.zeros(T)
    terms_trade = np.zeros(T)
    health_crisis = np.zeros(T)

    name = scenario_name.lower().strip()

    if name in ("baseline", "base_estable", "linea_base"):
        # Escenario 1: Línea base estable (sin perturbaciones exógenas)
        pass

    elif name in ("global_recession", "recesion_global"):
        # Escenario 2: Recesión global sincronizada (años 6-8 y 20-21)
        demand[5:8] = -0.08
        demand[19:22] = -0.06
        terms_trade[5:8] = -0.10
        spread[5:8] = 0.025

    elif name in ("commodity_shock", "choque_commodities"):
        # Escenario 3: Choque severo de términos de intercambio / materias primas (años 8-12)
        terms_trade[7:12] = -0.25
        demand[7:12] = -0.04
        spread[7:12] = 0.030

    elif name in ("pandemic", "pandemia"):
        # Escenario 4: Pandemia global con cuarentenas y disrupción productiva (años 10-12)
        health_crisis[9:11] = 1.0
        health_crisis[11:13] = 0.4
        demand[9:11] = -0.12
        demand[11:13] = -0.03
        labor[9:11] = -0.035
        spread[9:12] = 0.035

    elif name in ("aging_demographic", "envejecimiento"):
        # Escenario 5: Envejecimiento demográfico acelerado (declive de fuerza laboral desde año 7)
        for t in range(6, T):
            aging_factor = (t - 6) / (T - 6)
            labor[t] = -0.015 * aging_factor

    elif name in ("ai_disruption", "disrupcion_ia"):
        # Escenario 6: Disrupción tecnológica por Automatización e Inteligencia Artificial (desde año 5)
        # Aumenta fuertemente la productividad TFP pero genera fricción laboral inicial
        for t in range(4, T):
            ai_factor = min(1.0, (t - 4) / 8.0)
            tfp[t] = 0.045 * ai_factor
            # Desplazamiento transitorio en el empleo si no hay adaptación
            if t < 12:
                demand[t] = -0.02

    elif name in ("debt_crisis", "crisis_deuda"):
        # Escenario 7: Crisis de confianza soberana y repentino frenazo de flujos de capital (años 12-16)
        spread[11:16] = 0.065  # +650 bps de prima de riesgo
        demand[11:15] = -0.07
        terms_trade[11:14] = -0.08

    else:
        raise ValueError(f"Escenario no reconocido: '{scenario_name}'.")

    return {
        "tfp": tfp,
        "demand": demand,
        "spread": spread,
        "labor": labor,
        "terms_trade": terms_trade,
        "health_crisis": health_crisis,
    }

ALL_SCENARIOS = [
    "baseline",
    "global_recession",
    "commodity_shock",
    "pandemic",
    "aging_demographic",
    "ai_disruption",
    "debt_crisis",
]
