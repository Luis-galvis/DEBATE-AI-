"""
Capa de Adaptadores de Datos y Visualización para el Dashboard.
"""
from src.app.viz.metrics_catalog import METRICS_CATALOG, COLOR_PALETTE, SYSTEM_LABELS
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
    generate_monte_carlo_trajectories,
)
from src.app.viz.findings_generator import generate_automated_findings
from src.app.viz.export_helper import export_plotly_figure, create_video_assets_zip
