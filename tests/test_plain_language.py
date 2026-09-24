"""
Pruebas Unitarias para la Capa Pedagógica de Lenguaje Sencillo (tests/test_plain_language.py).
Valida:
1. Integridad del glosario central (glossary.yaml) y esquemas Pydantic.
2. Ausencia de jerga prohibida en modo Simple.
3. Nivel de legibilidad en español (índice Fernández-Huerta / INFLESZ >= 55.0).
4. Compatibilidad de argumentos en run_pareto_optimization.
"""

import pytest
from src.app.viz.glossary_loader import (
    get_glossary,
    format_help_card,
    generate_chart_footer,
    calculate_readability_score,
)
from src.app.viz.metrics_catalog import METRICS_CATALOG
from src.simulation.policy_vector import POLICY_DIMENSIONS
from src.optimization.pareto_optimizer import run_pareto_optimization

FORBIDDEN_JARGON_SIMPLE = [
    "nsga",
    "topsis",
    "mpc",
    "tfp",
    "p10",
    "p90",
    "kakwani",
    "autarquía",
    "cobb-douglas",
    "baricéntrico",
    "svd",
]

def test_glossary_schema_and_integrity():
    """Verifica que el glosario cargue y valide todas las entradas correctamente."""
    glossary = get_glossary()
    entries = glossary.get_all()
    assert len(entries) >= 15

    for entry in entries:
        assert entry.id
        assert entry.nombre_simple
        assert entry.nombre_tecnico
        assert entry.categoria
        assert entry.definicion_corta
        assert len(entry.definicion_corta.split()) <= 25, f"Definición de {entry.id} supera las 25 palabras"
        assert entry.analogia_cotidiana
        assert entry.como_leerlo
        assert entry.por_que_importa
        assert entry.lo_que_no_mide

def test_forbidden_jargon_in_simple_mode():
    """Verifica que el modo simple no contenga siglas o términos sin explicar."""
    glossary = get_glossary()
    for entry in glossary.get_all():
        simple_text = (entry.nombre_simple + " " + entry.definicion_corta).lower()
        for jargon in FORBIDDEN_JARGON_SIMPLE:
            assert jargon not in simple_text, f"Jerga prohibida '{jargon}' encontrada en modo simple para {entry.id}"

def test_spanish_readability_score():
    """Verifica que las definiciones alcancen un nivel de legibilidad 'Normal' o superior (>= 55.0)."""
    glossary = get_glossary()
    scores = []
    for entry in glossary.get_all():
        res = calculate_readability_score(entry.definicion_corta)
        scores.append(res["score"])
        assert res["score"] >= 50.0, f"Definición de {entry.id} tiene legibilidad baja ({res['score']})"

    avg_score = sum(scores) / len(scores)
    assert avg_score >= 55.0, f"Promedio de legibilidad {avg_score:.1f} inferior al umbral normal"

def test_chart_footers_generation():
    """Verifica que los pies de gráfico contengan las 3 secciones requeridas."""
    footers = generate_chart_footer("pca_trajectories")
    assert "what_you_see" in footers
    assert "how_to_read" in footers
    assert "watch_out" in footers

def test_pareto_optimizer_arguments_fix():
    """Verifica que run_pareto_optimization acepte calibration_country y random_seed."""
    res = run_pareto_optimization(
        calibration_country="Colombia",
        n_gen=2,
        pop_size=10,
        random_seed=42,
    )
    assert "F" in res
    assert "X" in res
    assert len(res["F"]) > 0
