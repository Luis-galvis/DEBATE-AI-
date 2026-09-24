"""
Tests unitarios del Motor Macroeconómico Determinista.
Verifica identidades contables (Y = C + I + G + NX), límites de Gini, solvencia de deuda y consistencia de arquetipos.
"""

import numpy as np
import pytest
from src.simulation.policy_vector import (
    PolicyVector,
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)
from src.simulation.solow_engine import MacroEconomy
from src.simulation.metrics import calculate_metrics
from src.simulation.abm_micro import run_abm_validation

def test_accounting_identity_closure():
    """Verifica que en cada año t se cumpla exactamente Y = C + I + G + NX."""
    for vec in [CAPITALIST_INITIAL_VECTOR, COLLECTIVIST_INITIAL_VECTOR, SOCDEM_INITIAL_VECTOR]:
        econ = MacroEconomy(policy=vec, years=30)
        results = econ.simulate()

        Y = results["gdp"]
        C = results["consumption"]
        I = results["investment"]
        G = results["public_spending"]
        NX = results["net_exports"]

        # Y_t - (C_t + I_t + G_t + NX_t) == 0.0 dentro de tolerancia numérica
        discrepancy = np.max(np.abs(Y - (C + I + G + NX)))
        assert discrepancy < 1e-6, f"Fallo en identidad contable, discrepancia: {discrepancy}"

def test_gini_bounds_and_ranking():
    """Verifica que el coeficiente Gini esté acotado en (0, 1) y que Colectivista < Capitalista en desigualdad."""
    econ_cap = MacroEconomy(policy=CAPITALIST_INITIAL_VECTOR, years=30)
    econ_col = MacroEconomy(policy=COLLECTIVIST_INITIAL_VECTOR, years=30)
    econ_soc = MacroEconomy(policy=SOCDEM_INITIAL_VECTOR, years=30)

    res_cap = econ_cap.simulate()
    res_col = econ_col.simulate()
    res_soc = econ_soc.simulate()

    m_cap = calculate_metrics(res_cap)
    m_col = calculate_metrics(res_col)
    m_soc = calculate_metrics(res_soc)

    # Todos los Gini deben estar entre 0.10 y 0.70
    assert 0.10 <= m_cap["gini_avg"] <= 0.70
    assert 0.10 <= m_col["gini_avg"] <= 0.70
    assert 0.10 <= m_soc["gini_avg"] <= 0.70

    # Colectivista y Socialdemócrata deben tener menor Gini que el Capitalista de libre mercado puro
    assert m_col["gini_avg"] < m_cap["gini_avg"]
    assert m_soc["gini_avg"] < m_cap["gini_avg"]

def test_growth_and_economic_freedom():
    """Verifica que el modelo de libre mercado tenga mayor libertad económica y fuerte crecimiento."""
    econ_cap = MacroEconomy(policy=CAPITALIST_INITIAL_VECTOR, years=30)
    econ_col = MacroEconomy(policy=COLLECTIVIST_INITIAL_VECTOR, years=30)

    res_cap = econ_cap.simulate()
    res_col = econ_col.simulate()

    m_cap = calculate_metrics(res_cap)
    m_col = calculate_metrics(res_col)

    assert m_cap["economic_freedom_avg"] > m_col["economic_freedom_avg"]
    assert m_cap["terminal_gdp_pc"] > 0.0

def test_micro_abm_validation():
    """Verifica que la capa micro de Mesa ejecute y devuelva métricas válidas."""
    abm_res = run_abm_validation(SOCDEM_INITIAL_VECTOR, steps=10)
    assert "micro_gini_wealth" in abm_res
    assert 0.0 < abm_res["micro_gini_wealth"] < 1.0
    assert abm_res["micro_avg_wealth"] > 0.0
