"""
Pruebas Unitarias para los Adaptadores de Datos y Visualización (src/app/viz/).
Verifica la transformación robusta de datos para gráficos y casos límite.
"""

import pytest
import pandas as pd
import numpy as np

from src.app.viz.metrics_catalog import METRICS_CATALOG, COLOR_PALETTE
from src.app.viz.debate_adapter import (
    load_debate_session_data,
    get_rounds_count,
    extract_round_dialogues,
    get_policy_vectors_evolution,
    compute_pca_trajectory,
    compute_convergence_curve,
    extract_concessions_data,
    extract_referee_rubric_history,
)
from src.app.viz.simulation_adapter import (
    get_archetype_and_consensus_vectors,
    run_multi_position_simulations,
    compute_all_metrics_table,
    compute_normalized_radar_data,
    compute_shock_resilience_comparison,
)
from src.app.viz.findings_generator import generate_automated_findings

def test_metrics_catalog_integrity():
    """Verifica que el catálogo de métricas contenga todos los campos requeridos."""
    assert len(METRICS_CATALOG) >= 15
    for key, info in METRICS_CATALOG.items():
        assert "name" in info
        assert "unit" in info
        assert "direction" in info
        assert "better_is_higher" in info
        assert "formula" in info
        assert "source" in info

def test_debate_adapter_normal_session():
    """Verifica la carga y procesamiento de la sesión de debate."""
    session_data = load_debate_session_data()
    assert isinstance(session_data, dict)
    
    rounds_cnt = get_rounds_count(session_data)
    assert rounds_cnt >= 0
    
    # Proyección PCA
    df_pca, var_x, var_y = compute_pca_trajectory(session_data)
    assert isinstance(df_pca, pd.DataFrame)
    if not df_pca.empty:
        assert "pca_x" in df_pca.columns
        assert "pca_y" in df_pca.columns
        assert var_x >= 0.0
        assert var_y >= 0.0
        
    # Curva de convergencia
    df_conv = compute_convergence_curve(session_data)
    assert isinstance(df_conv, pd.DataFrame)
    if not df_conv.empty:
        assert "mean_distance" in df_conv.columns
        assert (df_conv["mean_distance"] >= 0).all()

def test_debate_adapter_edge_cases():
    """Verifica el comportamiento robusto ante datos vacíos o incompletos."""
    empty_session = {"metadata": {}, "rounds": []}
    assert get_rounds_count(empty_session) == 0
    
    dialogue = extract_round_dialogues(empty_session, 1)
    assert dialogue["speeches"] == []
    
    df_pca, vx, vy = compute_pca_trajectory(empty_session)
    assert vx >= 0.0
    assert vy >= 0.0
    
    df_conc = extract_concessions_data(empty_session)
    assert isinstance(df_conc, pd.DataFrame)

def test_simulation_adapter_execution():
    """Verifica la ejecución de simulación de las 4 posiciones."""
    vectors = get_archetype_and_consensus_vectors()
    assert len(vectors) == 4
    assert "consensus" in vectors
    
    sim_res = run_multi_position_simulations(vectors, calibration_country="Colombia", scenario="baseline")
    assert len(sim_res) == 4
    
    df_metrics = compute_all_metrics_table(sim_res)
    assert not df_metrics.empty
    assert "consensus" in df_metrics.columns
    assert "capitalist" in df_metrics.columns
    
    df_radar = compute_normalized_radar_data(df_metrics)
    assert not df_radar.empty
    for col in ["capitalist", "collectivist", "socdem", "consensus"]:
        assert (df_radar[col] >= 0.0).all()
        assert (df_radar[col] <= 100.0).all()

def test_automated_findings_generation():
    """Verifica que el generador de hallazgos devuelva entre 5 y 8 observaciones."""
    session_data = load_debate_session_data()
    vectors = get_archetype_and_consensus_vectors(session_data)
    sim_res = run_multi_position_simulations(vectors, calibration_country="Colombia", scenario="baseline")
    df_metrics = compute_all_metrics_table(sim_res)
    df_resil = compute_shock_resilience_comparison(vectors, calibration_country="Colombia")
    
    findings = generate_automated_findings(df_metrics, session_data, df_resil)
    assert len(findings) >= 5
    assert len(findings) <= 8
    for fd in findings:
        assert "title" in fd
        assert "insight" in fd
        assert "target_view" in fd
