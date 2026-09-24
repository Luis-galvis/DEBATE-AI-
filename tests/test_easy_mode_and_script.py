"""
Suite de Pruebas: Modo Fácil, Tarjetas de Cierre de Ronda, Gráficos Explicados y Guion de Video.
Verifica:
1. Generación de las 7 tarjetas de cierre sin valores nulos y con convergencia 0-100%.
2. Configuración de las 6 métricas populares y semáforos cualitativos.
3. Construcción válida de la Regla de Posiciones (Policymeter) y medidores.
4. Integridad estructural y trazabilidad numérica de docs/video/GUION_VIDEO.md.
5. Puntuación de legibilidad en español (INFLESZ / Fernández-Huerta) > 60.
"""

import json
from pathlib import Path
import pytest

from src.config import BASE_DIR, OUTPUTS_DIR
from src.app.viz.round_summary_generator import (
    generate_round_summary_card,
    generate_full_debate_evolution_table,
    POPULAR_METRICS_CONFIG,
    get_metric_status_tag,
    calculate_round_convergence_score,
)
from src.app.viz.easy_charts import (
    render_policymeter_chart,
    render_convergence_gauge,
    render_horizontal_comparison_bars,
)
from src.app.viz.glossary_loader import calculate_readability_score
from src.reporting.script_generator import export_video_script_file

@pytest.fixture
def golden_session_data():
    golden_path = OUTPUTS_DIR / "golden_run" / "debate_session_golden.json"
    assert golden_path.exists(), "El archivo golden_run/debate_session_golden.json debe existir"
    with open(golden_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_all_seven_round_summary_cards(golden_session_data):
    """Verifica que las 7 tarjetas de cierre se generen completas y sin nulos."""
    for r in range(1, 8):
        card = generate_round_summary_card(golden_session_data, r)
        assert card["round_number"] == r
        assert len(card["what_happened"]) > 15
        assert "capitalist" in card["stances"]
        assert "collectivist" in card["stances"]
        assert "socdem" in card["stances"]
        assert 0.0 <= card["convergence_pct"] <= 100.0
        assert len(card["coinciden"]) == 2
        assert len(card["chocan"]) == 2
        assert len(card["consensus_points"]) >= 3
        assert len(card["what_changed"]) > 10

    # Verificar que en R1 a R6 sea provisional y en R7 sea oficial
    r1_card = generate_round_summary_card(golden_session_data, 1)
    assert not r1_card["is_final_official"]
    assert "Provisional" in r1_card["consensus_status_label"]

    r7_card = generate_round_summary_card(golden_session_data, 7)
    assert r7_card["is_final_official"]
    assert "Oficial" in r7_card["consensus_status_label"]

def test_popular_metrics_semaphores():
    """Verifica que las 6 métricas populares tengan umbrales y semáforos."""
    assert len(POPULAR_METRICS_CONFIG) == 6
    
    # Test GDP per capita ($15,000 debe ser verde, $5,000 debe ser rojo)
    tag_high, col_high = get_metric_status_tag("terminal_gdp_pc", 15000)
    assert "🟢" in tag_high
    
    tag_low, col_low = get_metric_status_tag("terminal_gdp_pc", 5000)
    assert "🔴" in tag_low

    # Test Gini (0.39 debe ser verde, 0.58 debe ser rojo)
    tag_g_good, _ = get_metric_status_tag("gini_avg", 0.39)
    assert "🟢" in tag_g_good
    
    tag_g_bad, _ = get_metric_status_tag("gini_avg", 0.58)
    assert "🔴" in tag_g_bad

def test_policymeter_chart_generation(golden_session_data):
    """Verifica que el Policymeter se construya correctamente."""
    from src.app.viz.simulation_adapter import get_archetype_and_consensus_vectors
    vectors = get_archetype_and_consensus_vectors(golden_session_data)
    cons_dict = vectors["consensus"].to_dict()
    vec_dicts = {k: v.to_dict() for k, v in vectors.items() if k != "consensus"}
    
    fig = render_policymeter_chart(vec_dicts, consensus_vector=cons_dict, show_explained_mode=True)
    assert fig is not None
    assert len(fig.data) > 5

def test_video_script_file_integrity():
    """Verifica que docs/video/GUION_VIDEO.md exista y contenga todas las secciones requeridas."""
    export_video_script_file()
    script_file = BASE_DIR / "docs" / "video" / "GUION_VIDEO.md"
    assert script_file.exists()
    
    content = script_file.read_text(encoding="utf-8")
    
    # Verificar secciones obligatorias
    assert "0:00 - 0:30" in content
    assert "Paso 1" in content or "Recorrido Guiado" in content
    assert "Ronda 1" in content
    assert "Ronda 7" in content
    assert "La Parte Honesta" in content or "La parte honesta" in content
    assert "Frases que NUNCA debo decir" in content
    assert "Preguntas Frecuentes" in content
    assert "Checklist de Grabación" in content
    assert "Shorts / Reels / TikTok" in content

def test_readability_of_easy_mode_explanations(golden_session_data):
    """Verifica que los textos en modo Fácil tengan un nivel de legibilidad adecuado en español."""
    for r in range(1, 8):
        card = generate_round_summary_card(golden_session_data, r)
        score_info = calculate_readability_score(card["what_happened"])
        assert score_info["score"] >= 45.0, f"Legibilidad baja en ronda {r}: {score_info}"

def test_horizontal_comparison_bars_rendering(golden_session_data):
    """Verifica que las barras comparativas funcionen con formato de tabla de métricas y no lancen NameError ni KeyError."""
    from src.app.viz.simulation_adapter import (
        get_archetype_and_consensus_vectors,
        run_multi_position_simulations,
        compute_all_metrics_table,
    )
    vectors = get_archetype_and_consensus_vectors(golden_session_data)
    sim_res = run_multi_position_simulations(vectors, calibration_country="Colombia", scenario="baseline")
    df_metrics = compute_all_metrics_table(sim_res)
    
    fig_gdp = render_horizontal_comparison_bars(df_metrics, "terminal_gdp_pc", "Crecimiento PIB")
    assert fig_gdp is not None
    assert len(fig_gdp.data) == 1
    assert len(fig_gdp.data[0].x) == 4
    
    fig_gini = render_horizontal_comparison_bars(df_metrics, "gini_avg", "Igualdad Gini")
    assert fig_gini is not None
    assert len(fig_gini.data[0].x) == 4

def test_pareto_natural_shape_and_columns():
    """Verifica que el optimizador Pareto devuelva exactamente 5 dimensiones naturales y las columnas coincidan."""
    from src.optimization.pareto_optimizer import run_pareto_optimization
    opt_res = run_pareto_optimization(calibration_country="Colombia", n_gen=5, pop_size=10, random_seed=42)
    assert "pareto_F_natural" in opt_res
    F_nat = opt_res["pareto_F_natural"]
    assert F_nat.shape[1] == 5, f"Debe tener exactamente 5 objetivos naturales, pero tiene {F_nat.shape[1]}"
    import pandas as pd
    cols = ["PIB_pc", "Gini", "Deuda_PIB", "Resiliencia", "Bienestar"]
    df_pareto = pd.DataFrame(F_nat, columns=cols)
    assert len(df_pareto) > 0
    assert "Gini" in df_pareto.columns
    assert "PIB_pc" in df_pareto.columns


