"""
Tests unitarios para el Orquestador del Debate de 7 Rondas.
"""

import pytest
from src.agents.orchestrator import DebateOrchestrator

def test_orchestrator_initialization():
    orchestrator = DebateOrchestrator(calibration_country="colombia", execution_mode="record")
    assert orchestrator.capitalist.name == "El Capitalista"
    assert orchestrator.collectivist.name == "El Colectivista"
    assert orchestrator.socdem.name == "El Socialdemócrata"
    assert len(orchestrator.vectors) == 3

def test_orchestrator_round_1_and_2():
    orchestrator = DebateOrchestrator(calibration_country="colombia", execution_mode="record")
    r1 = orchestrator.run_round_1_opening()
    assert r1["round"] == 1
    assert len(r1["turns"]) == 3

    r2 = orchestrator.run_round_2_baseline_sim()
    assert r2["round"] == 2
    assert "sim_metrics" in r2
    assert len(r2["turns"]) == 3
