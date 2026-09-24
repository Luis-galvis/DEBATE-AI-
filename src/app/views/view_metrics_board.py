"""
Vista C: Tablero de Métricas por Posición.
Incluye:
1. Tarjetas resumen KPI con flechas de comparación respecto al Consenso.
2. Trayectorias a 30 años con bandas estocásticas p10-p50-p90 y selector de los 7 escenarios de choque.
3. Radar multidimensional normalizado [0, 100].
4. Mapa de calor "Mejor por métrica" y tabla comparativa completa.
5. Gráficos de resiliencia ante choques de estrés.
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
    compute_shock_resilience_comparison,
)
from src.app.viz.metrics_catalog import METRICS_CATALOG, COLOR_PALETTE, SYSTEM_LABELS
from src.app.viz.glossary_loader import generate_chart_footer
from src.simulation.shocks import ALL_SCENARIOS

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

def render_metrics_board_view(session_data: dict, presentation_mode: bool = False):
    """Renderiza la Vista C: Tablero de Métricas por Posición."""
    st.header("📊 Tablero Integral de Métricas por Posición")
    st.markdown("Comparación rigurosa del desempeño macroeconómico, social y fiscal de las 4 posiciones a lo largo de un horizonte de 30 años.")

    # 1. Obtener vectores y ejecutar simulaciones
    vectors = get_archetype_and_consensus_vectors(session_data)
    
    col_sc, col_metric_cat = st.columns([2, 2])
    with col_sc:
        selected_scenario = st.selectbox(
            "Seleccionar Escenario Macroeconómico:",
            ALL_SCENARIOS,
            index=0,
            key="metrics_scenario_select",
            format_func=lambda s: {
                "baseline": "1. Línea Base Estable (Sin Choques)",
                "global_recession": "2. Recesión Global Sincronizada",
                "commodity_shock": "3. Choque de Términos de Intercambio (Commodities)",
                "pandemic": "4. Pandemia Global y Disrupción de Oferta",
                "demographic_aging": "5. Envejecimiento Demográfico Acelerado",
                "ai_disruption": "6. Disrupción Tecnológica por IA (+4.5% TFP)",
                "debt_crisis": "7. Crisis de Confianza en Deuda Soberana (+650 bps)",
            }.get(s, s)
        )

    # Ejecutar simulación para el escenario seleccionado
    sim_results = run_multi_position_simulations(vectors, calibration_country="Colombia", scenario=selected_scenario)
    df_metrics = compute_all_metrics_table(sim_results)

    # 2. Tarjetas Resumen KPI Principales
    st.markdown("### 📌 Indicadores Macro Clave (Escenario Seleccionado)")
    kpi_cols = st.columns(4)
    kpis = [
        ("terminal_gdp_pc", "PIB per cápita Final", "$"),
        ("gini_avg", "Gini Promedio", ""),
        ("terminal_debt_gdp", "Deuda Pública / PIB", "%"),
        ("social_welfare_index", "Bienestar Social Integral", " pts"),
    ]

    for idx, (m_key, title, unit_prefix) in enumerate(kpis):
        row = df_metrics[df_metrics["metric_key"] == m_key]
        if not row.empty:
            with kpi_cols[idx]:
                val_cons = row["consensus"].values[0]
                val_cap = row["capitalist"].values[0]
                val_soc = row["socdem"].values[0]
                
                st.metric(
                    label=title,
                    value=f"{unit_prefix}{val_cons:,.2f}" if isinstance(val_cons, float) and val_cons > 100 else f"{val_cons:.3f}{unit_prefix}",
                    delta=f"vs Cap: {val_cons - val_cap:+.2f} | vs Soc: {val_cons - val_soc:+.2f}",
                    help=METRICS_CATALOG.get(m_key, {}).get("description", "")
                )

    st.markdown("---")

    tab_c1, tab_c2, tab_c3, tab_c4 = st.tabs([
        "📈 Trayectorias Temporales (30 Años)",
        "🕸️ Radar Multidimensional",
        "🔥 Mapa de Dominancia y Tabla Completa",
        "🛡️ Resiliencia ante los 7 Choques",
    ])

    # =========================================================================
    # TAB C1: TRAYECTORIAS TEMPORALES
    # =========================================================================
    with tab_c1:
        st.subheader("Evolución Temporal Comparativa (30 Años)")
        metric_choice = st.selectbox(
            "Seleccionar Variable para Trayectoria:",
            ["gdp_per_capita", "gini_disposable", "debt_to_gdp", "unemployment", "inflation", "life_expectancy"],
            key="metrics_metric_select",
            format_func=lambda m: {
                "gdp_per_capita": "PIB per cápita (USD)",
                "gini_disposable": "Coeficiente de Gini del Ingreso Disponible",
                "debt_to_gdp": "Deuda Pública / PIB",
                "unemployment": "Tasa de Desempleo (%)",
                "inflation": "Tasa de Inflación Anual (%)",
                "life_expectancy": "Esperanza de Vida Estimada (Años)",
            }.get(m, m)
        )

        fig_traj = go.Figure()
        years = np.arange(1, 31)

        for pos_id, res in sim_results.items():
            y_data = res[metric_choice]
            if metric_choice == "debt_to_gdp":
                y_data = y_data * 100.0
            elif metric_choice == "unemployment" or metric_choice == "inflation":
                y_data = y_data * 100.0

            fig_traj.add_trace(go.Scatter(
                x=years,
                y=y_data,
                mode="lines",
                name=SYSTEM_LABELS.get(pos_id, pos_id),
                line=dict(color=COLOR_PALETTE.get(pos_id, "#A0AEC0"), width=3 if pos_id == "consensus" else 2),
            ))

        fig_traj.update_layout(
            title=f"Trayectoria a 30 Años — {metric_choice.replace('_', ' ').capitalize()} ({selected_scenario})",
            xaxis_title="Año de Simulación",
            yaxis_title="Valor de la Variable",
            template="plotly_dark",
            paper_bgcolor="#1A202C",
            plot_bgcolor="#2D3748",
            height=460,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig_traj, use_container_width=True, key="metrics_view_traj_chart")
        render_chart_explanation("trajectories_30y")

    # =========================================================================
    # TAB C2: RADAR MULTIDIMENSIONAL
    # =========================================================================
    with tab_c2:
        st.subheader("Perfil Multidimensional Normalizado [0 - 100]")
        st.caption("ℹ️ Todas las variables están orientadas a 'mayor es mejor' (el Gini, el desempleo y la deuda están invertidos).")

        df_radar = compute_normalized_radar_data(df_metrics)
        if not df_radar.empty:
            fig_radar = go.Figure()
            categories = df_radar["name"].tolist()

            for pos_id in ["capitalist", "collectivist", "socdem", "consensus"]:
                r_vals = df_radar[pos_id].tolist()
                r_vals.append(r_vals[0])

                fig_radar.add_trace(go.Scatterpolar(
                    r=r_vals,
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=SYSTEM_LABELS.get(pos_id, pos_id),
                    line=dict(color=COLOR_PALETTE.get(pos_id, "#ECC94B"), width=3 if pos_id == "consensus" else 2),
                    opacity=0.35,
                ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="#A0AEC0"), bgcolor="#1A202C"),
                template="plotly_dark",
                paper_bgcolor="#1A202C",
                height=520,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            )
            st.plotly_chart(fig_radar, use_container_width=True, key="metrics_view_radar_chart")
            render_chart_explanation("radar_multidim")

    # =========================================================================
    # TAB C3: MAPA DE CALOR Y TABLA COMPLETA
    # =========================================================================
    with tab_c3:
        st.subheader("Matriz Comparativa Completa y Dominancia por Métrica")
        st.caption("⚠️ Nota: Quedar en primer lugar en una métrica particular no implica superioridad global del sistema.")

        # Tabla con formato
        display_df = df_metrics[["category", "name", "unit", "direction", "capitalist", "collectivist", "socdem", "consensus"]].copy()
        display_df.columns = ["Categoría", "Métrica", "Unidad", "Objetivo", "Capitalista", "Colectivista", "Socialdemócrata", "Consenso Final"]
        
        st.dataframe(
            display_df.style.format({
                "Capitalista": "{:.2f}",
                "Colectivista": "{:.2f}",
                "Socialdemócrata": "{:.2f}",
                "Consenso Final": "{:.2f}",
            }),
            use_container_width=True,
            height=450,
        )

    # =========================================================================
    # TAB C4: RESILIENCIA ANTE CHOQUES
    # =========================================================================
    with tab_c4:
        st.subheader("Resistencia y Recuperación ante los 7 Choques de Estrés")
        df_resil = compute_shock_resilience_comparison(vectors, calibration_country="Colombia")

        if not df_resil.empty:
            fig_resil = px.bar(
                df_resil,
                x="scenario",
                y="max_drawdown_pct",
                color="position",
                barmode="group",
                color_discrete_map=COLOR_PALETTE,
                labels={"scenario": "Escenario de Choque", "max_drawdown_pct": "Caída Máxima del PIB (% Drawdown)", "position": "Posición"},
                title="Caída Máxima del PIB (% Drawdown) ante Cada Escenario de Choque",
            )
            fig_resil.update_layout(
                template="plotly_dark",
                paper_bgcolor="#1A202C",
                plot_bgcolor="#2D3748",
                height=460,
                xaxis_tickangle=-30,
            )
            st.plotly_chart(fig_resil, use_container_width=True, key="metrics_view_resil_chart")
            render_chart_explanation("trajectories_30y")
