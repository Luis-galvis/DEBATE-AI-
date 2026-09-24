"""
Vista B: Mapa de Posiciones y Convergencia.
Incluye:
1. Proyección 2D del espacio de políticas (PCA con varianza explicada y flechas de trayectoria).
2. Gráfico de Coordenadas Paralelas de las 10 dimensiones con selector de ronda.
3. Curva de Convergencia (distancia euclídea vs umbral epsilon).
4. Gráfico de Concesiones (barras divergentes por parámetro y líneas rojas).
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.app.viz.debate_adapter import (
    compute_pca_trajectory,
    get_policy_vectors_evolution,
    compute_convergence_curve,
    extract_concessions_data,
)
from src.app.viz.metrics_catalog import COLOR_PALETTE, SYSTEM_LABELS
from src.app.viz.glossary_loader import generate_chart_footer
from src.simulation.policy_vector import POLICY_DIMENSIONS

def render_chart_explanation(chart_id: str, context_data: dict = None):
    """Renderiza el bloque de 3 líneas pedagógicas debajo del gráfico."""
    footer = generate_chart_footer(chart_id, context_data)
    st.markdown(f"""
    <div style="background-color: #2D3748; padding: 12px 16px; border-radius: 6px; border-left: 4px solid #3182CE; margin-top: 10px; font-size: 0.88rem; line-height: 1.5; color: #E2E8F0;">
        <b>👀 Qué estás viendo:</b> {footer['what_you_see']}<br>
        <b>🧭 Cómo leerlo:</b> {footer['how_to_read']}<br>
        <b>⚠️ Ojo con esto:</b> {footer['watch_out']}
    </div>
    """, unsafe_allow_html=True)

def render_positions_convergence_view(session_data: dict, presentation_mode: bool = False):
    """Renderiza la Vista B: Mapa de Posiciones y Convergencia."""
    st.header("🗺️ Mapa de Posiciones y Dinámica de Convergencia")
    st.markdown("Visualiza cómo evolucionan las propuestas de los agentes en el hiperespacio de políticas de 10 dimensiones hacia el consenso final.")

    tab_b1, tab_b2, tab_b3, tab_b4 = st.tabs([
        "📍 Proyección PCA 2D y Trayectorias",
        "🎛️ Coordenadas Paralelas (10D)",
        "📉 Curva de Convergencia (Épsilon)",
        "🔄 Concesiones y Líneas Rojas",
    ])

    # =========================================================================
    # TAB B1: PROYECCIÓN PCA 2D
    # =========================================================================
    with tab_b1:
        st.subheader("Trayectoria de Negociación en 2D (Análisis de Componentes Principales)")
        st.caption("ℹ️ Nota Metodológica: El hiperespacio de 10 políticas se reduce a 2 dimensiones ortogonales principales. Esta proyección ilustra proximidad relativa pero pierde una porción menor de varianza.")

        df_pca, var_x, var_y = compute_pca_trajectory(session_data)
        if not df_pca.empty and "pca_x" in df_pca.columns:
            st.info(f"📊 **Varianza Explicada**: Componente 1 (Eje X): **{var_x:.1f}%** | Componente 2 (Eje Y): **{var_y:.1f}%** | Varianza Total Acumulada: **{(var_x + var_y):.1f}%**")

            fig_pca = go.Figure()

            # Dibujar trayectorias de cada agente
            for ag_id in ["capitalist", "collectivist", "socdem"]:
                df_ag = df_pca[df_pca["agent"] == ag_id].sort_values("round")
                if len(df_ag) > 0:
                    fig_pca.add_trace(go.Scatter(
                        x=df_ag["pca_x"],
                        y=df_ag["pca_y"],
                        mode="lines+markers+text",
                        name=SYSTEM_LABELS.get(ag_id, ag_id),
                        text=[f"R{r}" if r > 0 else "Inicio" for r in df_ag["round"]],
                        textposition="top center",
                        line=dict(color=COLOR_PALETTE.get(ag_id, "#A0AEC0"), width=3, dash="solid"),
                        marker=dict(size=9, symbol="circle"),
                    ))

            # Dibujar punto de consenso si existe
            df_cons = df_pca[df_pca["agent"] == "consensus"]
            if not df_cons.empty:
                fig_pca.add_trace(go.Scatter(
                    x=df_cons["pca_x"],
                    y=df_cons["pca_y"],
                    mode="markers+text",
                    name="Consenso Final (Punto Medio)",
                    text=["🏆 Consenso"],
                    textposition="bottom center",
                    marker=dict(size=16, color=COLOR_PALETTE.get("consensus", "#ECC94B"), symbol="star"),
                ))

            fig_pca.update_layout(
                title="Desplazamiento de Posturas en el Espacio de Políticas (PCA 2D)",
                xaxis_title=f"Componente Principal 1 ({var_x:.1f}% var)",
                yaxis_title=f"Componente Principal 2 ({var_y:.1f}% var)",
                template="plotly_dark",
                paper_bgcolor="#1A202C",
                plot_bgcolor="#2D3748",
                height=520,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            )
            st.plotly_chart(fig_pca, use_container_width=True, key="positions_view_pca_chart")
            render_chart_explanation("pca_trajectories")
        else:
            st.warning("No hay suficientes datos de rondas para calcular la proyección PCA.")

    # =========================================================================
    # TAB B2: COORDENADAS PARALELAS
    # =========================================================================
    with tab_b2:
        st.subheader("Explorador Multidimensional de Políticas (10 Dimensiones)")
        
        df_evol = get_policy_vectors_evolution(session_data)
        if not df_evol.empty:
            available_rounds = sorted(df_evol["round"].unique())
            sel_round = st.selectbox(
                "Filtrar por Ronda:",
                available_rounds,
                index=len(available_rounds)-1,
                format_func=lambda r: f"Ronda {r}" if r > 0 else "Posición Inicial (Ronda 0)",
                key="positions_round_select",
            )

            df_filtered = df_evol[df_evol["round"] == sel_round].copy()
            df_filtered["agent_num"] = df_filtered["agent"].map({"capitalist": 0, "collectivist": 1, "socdem": 2, "consensus": 3}).fillna(0)

            dimensions_config = [
                dict(range=[0, 1], label=dim.replace("_", "<br>"), values=df_filtered[dim])
                for dim in POLICY_DIMENSIONS
            ]

            fig_par = go.Figure(data=go.Parcoords(
                line=dict(
                    color=df_filtered["agent_num"],
                    colorscale=[
                        [0.0, COLOR_PALETTE["capitalist"]],
                        [0.33, COLOR_PALETTE["collectivist"]],
                        [0.66, COLOR_PALETTE["socdem"]],
                        [1.0, COLOR_PALETTE["consensus"]],
                    ],
                    showscale=False
                ),
                dimensions=dimensions_config
            ))

            fig_par.update_layout(
                title=f"Configuración de las 10 Dimensiones de Política — {f'Ronda {sel_round}' if sel_round > 0 else 'Estado Inicial'}",
                template="plotly_dark",
                paper_bgcolor="#1A202C",
                height=480,
                margin=dict(l=60, r=60, t=60, b=40),
            )
            st.plotly_chart(fig_par, use_container_width=True, key="positions_view_parcoords_chart")
            render_chart_explanation("pareto_cloud")

    # =========================================================================
    # TAB B3: CURVA DE CONVERGENCIA
    # =========================================================================
    with tab_b3:
        st.subheader("Curva de Convergencia y Distancia Inter-Agentes")
        df_conv = compute_convergence_curve(session_data)

        if not df_conv.empty:
            fig_conv = go.Figure()

            fig_conv.add_trace(go.Scatter(
                x=df_conv["round"],
                y=df_conv["mean_distance"],
                mode="lines+markers",
                name="Distancia Media Inter-Agentes",
                line=dict(color="#63B3ED", width=3),
                marker=dict(size=8),
            ))

            fig_conv.add_trace(go.Scatter(
                x=df_conv["round"],
                y=df_conv["max_distance"],
                mode="lines+markers",
                name="Distancia Máxima (Discrepancia Extrema)",
                line=dict(color="#FC8181", width=2, dash="dash"),
            ))

            # Línea de umbral epsilon
            fig_conv.add_hline(
                y=0.15,
                line_dash="dot",
                line_color="#ECC94B",
                annotation_text="Umbral de Compromiso Aceptable (ε = 0.15)",
                annotation_position="bottom right",
            )

            fig_conv.update_layout(
                title="Evolución de la Brecha Euclídea entre Posturas a lo Largo del Debate",
                xaxis_title="Número de Ronda",
                yaxis_title="Distancia Euclídea Media en Espacio [0, 1]^10",
                template="plotly_dark",
                paper_bgcolor="#1A202C",
                plot_bgcolor="#2D3748",
                height=420,
            )
            st.plotly_chart(fig_conv, use_container_width=True, key="positions_view_conv_chart")
            render_chart_explanation("pca_trajectories")

    # =========================================================================
    # TAB B4: CONCESIONES Y LÍNEAS ROJAS
    # =========================================================================
    with tab_b4:
        st.subheader("Concesiones por Parámetro: ¿Quién cedió qué?")
        df_conc = extract_concessions_data(session_data)

        if not df_conc.empty:
            fig_conc = px.bar(
                df_conc,
                x="dimension",
                y="delta",
                color="agent",
                barmode="group",
                color_discrete_map=COLOR_PALETTE,
                labels={"dimension": "Dimensión de Política", "delta": "Variación Neta (ΔX)", "agent": "Agente"},
                title="Desplazamiento Neto de Parámetros entre Posición Inicial y Final",
            )
            fig_conc.update_layout(
                template="plotly_dark",
                paper_bgcolor="#1A202C",
                plot_bgcolor="#2D3748",
                height=480,
                xaxis_tickangle=-45,
            )
            st.plotly_chart(fig_conc, use_container_width=True, key="positions_view_concessions_chart")
            render_chart_explanation("concessions_bars")

            st.markdown("""
            **Interpretación de Concesiones:**
            - **Valores positivos (+Δ)** indican incremento en intervención estatal, regulación o gasto.
            - **Valores negativos (-Δ)** indican desregulación, apertura comercial o restricción del gasto.
            - **Barras cercanas a 0** reflejan las líneas rojas que cada agente protegió intransigentemente.
            """)
