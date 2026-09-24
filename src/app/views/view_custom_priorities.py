"""
Vista E: Prioridades Personalizables (Simulador de Pesos Ponderados).
Permite al usuario definir la importancia relativa de 8 dimensiones macroeconómicas,
calculando en vivo el puntaje compuesto y ranking resultante para las 4 posiciones.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.app.viz.simulation_adapter import (
    get_archetype_and_consensus_vectors,
    run_multi_position_simulations,
    compute_all_metrics_table,
    compute_normalized_radar_data,
)
from src.app.viz.metrics_catalog import COLOR_PALETTE, SYSTEM_LABELS

def render_custom_priorities_view(session_data: dict, presentation_mode: bool = False):
    """Renderiza la Vista E: Prioridades Personalizables."""
    st.header("🎛️ Simulador de Preferencias Políticas: ¿Cuál 'Gana' según tus Valores?")
    st.markdown("Ajusta los ponderadores para ver cómo cambia el modelo preferido según las prioridades que elijas.")

    st.warning("""
    ⚠️ **NOTA METODOLÓGICA FUNDAMENTAL:**
    No existe un modelo económico 'objetivamente superior' en todas las dimensiones de forma universal.
    El resultado final depende intrínsecamente de los juicios de valor sobre cuánto peso otorgar al crecimiento vs. la igualdad, la estabilidad fiscal o las libertades individuales.
    """)

    # 1. Presets de Ponderación
    preset_choice = st.selectbox(
        "Cargar Perfil Predefinido (Preset):",
        ["Personalizado", "🚀 Máximo Crecimiento e Innovación", "🤝 Máxima Igualdad y Protección Social", "⚖️ Equilibrio Nórdico / Socialdemócrata", "🛡️ Máxima Resiliencia y Rigor Fiscal", "🗽 Libertades Económicas y Mercado"],
        index=0,
        key="custom_priorities_preset_select",
    )

    # Valores por defecto
    defaults = {
        "growth": 50, "equality": 50, "jobs": 50, "fiscal": 50,
        "resilience": 50, "welfare": 50, "freedom": 50, "environment": 50
    }

    if preset_choice == "🚀 Máximo Crecimiento e Innovación":
        defaults = {"growth": 90, "equality": 20, "jobs": 60, "fiscal": 70, "resilience": 40, "welfare": 40, "freedom": 90, "environment": 30}
    elif preset_choice == "🤝 Máxima Igualdad y Protección Social":
        defaults = {"growth": 30, "equality": 95, "jobs": 80, "fiscal": 30, "resilience": 60, "welfare": 90, "freedom": 20, "environment": 70}
    elif preset_choice == "⚖️ Equilibrio Nórdico / Socialdemócrata":
        defaults = {"growth": 70, "equality": 85, "jobs": 80, "fiscal": 80, "resilience": 80, "welfare": 90, "freedom": 75, "environment": 75}
    elif preset_choice == "🛡️ Máxima Resiliencia y Rigor Fiscal":
        defaults = {"growth": 50, "equality": 40, "jobs": 50, "fiscal": 95, "resilience": 95, "welfare": 60, "freedom": 60, "environment": 50}
    elif preset_choice == "🗽 Libertades Económicas y Mercado":
        defaults = {"growth": 85, "equality": 15, "jobs": 50, "fiscal": 75, "resilience": 45, "welfare": 35, "freedom": 100, "environment": 20}

    # 2. Sliders en 2 columnas
    st.markdown("### 🎚️ Ajuste de Pesos por Dimensión [0 - 100]")
    col_w1, col_w2 = st.columns(2)

    with col_w1:
        w_growth = st.slider("Crecimiento del PIB y Renta per Cápita", 0, 100, defaults["growth"], key="slider_w_growth")
        w_equality = st.slider("Reducción de Desigualdad (Gini) y Pobreza", 0, 100, defaults["equality"], key="slider_w_equality")
        w_jobs = st.slider("Creación de Empleo y Salarios Reales", 0, 100, defaults["jobs"], key="slider_w_jobs")
        w_fiscal = st.slider("Sostenibilidad Fiscal y Control de Deuda", 0, 100, defaults["fiscal"], key="slider_w_fiscal")

    with col_w2:
        w_resilience = st.slider("Resiliencia ante Choques Macroeconómicos", 0, 100, defaults["resilience"], key="slider_w_resilience")
        w_welfare = st.slider("Bienestar Social, Salud y Esperanza de Vida", 0, 100, defaults["welfare"], key="slider_w_welfare")
        w_freedom = st.slider("Libertades Económicas y Flexibilidad de Mercado", 0, 100, defaults["freedom"], key="slider_w_freedom")
        w_environment = st.slider("Sostenibilidad Ambiental (Menores Emisiones CO2)", 0, 100, defaults["environment"], key="slider_w_environment")

    # Normalizar pesos
    weights = np.array([w_growth, w_equality, w_jobs, w_fiscal, w_resilience, w_welfare, w_freedom, w_environment], dtype=float)
    total_w = np.sum(weights)
    if total_w == 0:
        weights = np.ones(8) / 8.0
    else:
        weights = weights / total_w

    # 3. Calcular simulación y puntajes normalizados
    vectors = get_archetype_and_consensus_vectors(session_data)
    sim_results = run_multi_position_simulations(vectors, calibration_country="Colombia", scenario="baseline")
    df_metrics = compute_all_metrics_table(sim_results)

    # Matriz de 8 variables clave normalizadas [0, 100]
    metric_keys = [
        "terminal_gdp_pc", "gini_avg", "unemployment_avg", "terminal_debt_gdp",
        "resilience_score", "social_welfare_index", "economic_freedom_avg", "total_co2"
    ]
    
    sub_df = df_metrics[df_metrics["metric_key"].isin(metric_keys)]
    scores = {"capitalist": 0.0, "collectivist": 0.0, "socdem": 0.0, "consensus": 0.0}

    for idx, key in enumerate(metric_keys):
        row = sub_df[sub_df["metric_key"] == key]
        if not row.empty:
            higher_better = row["better_is_higher"].values[0]
            vals = [row["capitalist"].values[0], row["collectivist"].values[0], row["socdem"].values[0], row["consensus"].values[0]]
            min_v = min(vals)
            max_v = max(vals)
            rng = max(1e-6, max_v - min_v)

            for p_id in scores.keys():
                v = row[p_id].values[0]
                norm_v = (v - min_v) / rng * 100.0 if higher_better else (max_v - v) / rng * 100.0
                scores[p_id] += norm_v * weights[idx]

    # 4. Mostrar Resultados Dinámicos
    st.markdown("---")
    st.subheader("🏆 Ranking Ponderado Resultante")

    df_rank = pd.DataFrame([
        {"Posición": SYSTEM_LABELS.get(p_id, p_id), "Puntaje Ponderado": round(sc, 1), "agent_id": p_id}
        for p_id, sc in scores.items()
    ]).sort_values("Puntaje Ponderado", ascending=False)

    col_rank_chart, col_rank_details = st.columns([3, 2])

    with col_rank_chart:
        fig_rank = px.bar(
            df_rank,
            x="Puntaje Ponderado",
            y="Posición",
            orientation="h",
            color="agent_id",
            color_discrete_map=COLOR_PALETTE,
            title="Puntaje Compuesto según Tus Preferencias [0 - 100]",
            text="Puntaje Ponderado",
        )
        fig_rank.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1A202C",
            plot_bgcolor="#2D3748",
            height=340,
            showlegend=False,
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_rank, use_container_width=True, key="custom_priorities_rank_chart")

    with col_rank_details:
        st.markdown("#### 🥇 Modelo Ganador:")
        winner = df_rank.iloc[0]
        st.success(f"**{winner['Posición']}** con un puntaje de **{winner['Puntaje Ponderado']} pts**.")
        st.caption("Prueba modificando los sliders para observar en qué punto exacto un modelo alternativo pasa al primer lugar.")
