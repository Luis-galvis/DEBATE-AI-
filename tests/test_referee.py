"""
Tests unitarios para el Árbitro-Auditor.
Verifica que audite intervenciones, detecte falacias/discrepancias y devuelva la rúbrica estructurada.
"""

import pytest
from src.agents.referee import RefereeAuditor
from src.simulation.policy_vector import CAPITALIST_INITIAL_VECTOR, SOCDEM_INITIAL_VECTOR
from src.agents.schemas import RefereeTurnEvaluation

def test_referee_audit_and_score():
    referee = RefereeAuditor()
    sim_data = {"terminal_gdp_pc": 185.4, "gini_avg": 0.42, "max_debt_gdp": 55.0}

    speech = (
        "Compañeros del consejo, de acuerdo con la simulación determinista a 30 años, "
        "nuestro PIB per cápita alcanzó 185.4 con una deuda pico del 55.0% del PIB. "
        "Reconocemos que nuestro coeficiente Gini se situó en 0.42, lo cual exige una red mínima de seguridad."
    )

    evaluation = referee.audit_and_score_turn(
        round_number=2,
        agent_name="El Capitalista",
        speech_text=speech,
        sim_data=sim_data,
        current_policy=CAPITALIST_INITIAL_VECTOR,
    )

    assert isinstance(evaluation, RefereeTurnEvaluation)
    assert 0.0 <= evaluation.total_score <= 10.0
    assert 0.0 <= evaluation.rigor_score <= 10.0
    assert evaluation.agent_evaluated == "El Capitalista"
