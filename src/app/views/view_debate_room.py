"""
Vista A: Sala de Debate (Línea de Tiempo Sincronizada).
Proporciona controles de reproducción (play, pausa, avanzar ronda), chat estructurado de intervenciones,
semáforo de fact-check del Árbitro y mini gráficos sincronizados en tiempo real.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.app.viz.debate_adapter import (
    get_rounds_count,
    extract_round_dialogues,
    get_policy_vectors_evolution,
)
from src.app.viz.metrics_catalog import COLOR_PALETTE, SYSTEM_LABELS
from src.simulation.policy_vector import POLICY_DIMENSIONS

def render_debate_room_view(session_data: dict, presentation_mode: bool = False):
    """Renderiza la Vista A: Sala de Debate sincronizada."""
    st.header("🎙️ Sala de Debate: Línea de Tiempo Sincronizada")
    st.markdown("Explora el diálogo interactivo ronda a ronda, los veredictos del Árbitro y la evolución de las políticas en tiempo real.")

    total_rounds = get_rounds_count(session_data)
    if total_rounds == 0:
        st.info("ℹ️ No hay sesiones de debate cargadas. Ejecuta un debate desde la barra lateral para comenzar.")
        return

    # 1. Controles tipo reproductor de medios
    st.markdown("### ⏯️ Control de Reproducción de Rondas")
    col_c1, col_c2, col_c3, col_c4 = st.columns([2, 1, 1, 3])
    
    if "active_debate_round" not in st.session_state:
        st.session_state["active_debate_round"] = 1
    else:
        st.session_state["active_debate_round"] = max(1, min(total_rounds, int(st.session_state["active_debate_round"])))

    def _prev_round():
        st.session_state["active_debate_round"] = max(1, int(st.session_state.get("active_debate_round", 1)) - 1)

    def _next_round():
        st.session_state["active_debate_round"] = min(total_rounds, int(st.session_state.get("active_debate_round", 1)) + 1)

    def _on_slider_change():
        if "_temp_round_slider" in st.session_state:
            st.session_state["active_debate_round"] = st.session_state["_temp_round_slider"]

    with col_c1:
        st.slider(
            "Seleccionar Ronda",
            min_value=1,
            max_value=total_rounds,
            value=st.session_state["active_debate_round"],
            key="_temp_round_slider",
            on_change=_on_slider_change,
            help="Desplaza la barra para viajar en el tiempo a cualquier ronda del debate."
        )

    selected_round = st.session_state["active_debate_round"]

    with col_c2:
        st.button("⏮️ Anterior", disabled=(selected_round <= 1), on_click=_prev_round, use_container_width=True, key="debate_room_prev_btn")

    with col_c3:
        st.button("Siguiente ⏭️", disabled=(selected_round >= total_rounds), on_click=_next_round, use_container_width=True, key="debate_room_next_btn")

    focus_text = "Discusión General"
    if session_data.get("rounds") and selected_round <= len(session_data["rounds"]):
        focus_text = session_data["rounds"][selected_round-1].get("focus", "Discusión General")

    with col_c4:
        st.markdown(f"**Visualizando:** `Ronda {selected_round} de {total_rounds}` | *Foco temático:* `{focus_text}`")

    st.markdown("---")

    # Extraer datos de la ronda seleccionada
    round_info = extract_round_dialogues(session_data, selected_round)
    speeches = round_info.get("speeches", [])
    ref_eval = round_info.get("referee", {})

    # Layout de 2 columnas: Izquierda (Chat de diálogo) | Derecha (Gráficos sincrónicos)
    col_chat, col_charts = st.columns([3, 2])

    with col_chat:
        st.subheader(f"💬 Intervenciones — {round_info['name']}")
        
        if not speeches:
            st.warning("No hay discursos registrados en esta ronda.")

        for sp in speeches:
            agent_id = sp["agent_id"]
            agent_color = sp["color"]
            avatar = sp["avatar"]
            agent_name = sp["agent_name"]
            content = sp["content"]
            claims = sp["claims"]

            with st.chat_message(name=agent_id, avatar=avatar):
                st.markdown(f"<span style='color:{agent_color}; font-weight:700; font-size:1.08rem;'>{avatar} {agent_name}</span> &nbsp; <span style='font-size:0.8rem; background-color:#2D3748; padding:2px 8px; border-radius:4px; color:#E2E8F0;'>Ronda {selected_round}</span>", unsafe_allow_html=True)
                
                # Renderizado limpio de Markdown (tablas, ecuaciones, negritas sin espacio blanco roto)
                st.markdown(content)

                # Resumen 'En simple' (máximo 30 palabras)
                simple_summaries = {
                    "capitalist": "💡 **En simple:** Defiende incentivos de libre mercado, bajos impuestos y rigor fiscal para acelerar la innovación y el crecimiento.",
                    "collectivist": "💡 **En simple:** Prioriza la propiedad social, protección laboral y transferencias universales para reducir la desigualdad y erradicar la pobreza.",
                    "socdem": "💡 **En simple:** Propone una economía mixta: mercado abierto y productivo combinado con un Estado de bienestar sólido e impuestos progresivos.",
                }
                summary_text = simple_summaries.get(agent_id, "💡 **En simple:** Propuesta de política económica orientada a mejorar el bienestar general.")
                st.info(summary_text)

                # Mostrar claims verificadas si existen
                if claims:
                    with st.expander(f"📊 Afirmaciones Cuantitativas Citadas ({len(claims)})", expanded=False):
                        for cl in claims:
                            m_name = cl.get("metric", "métrica")
                            val = cl.get("value", "N/A")
                            claim_type = cl.get("claim_type", "afirmación")
                            st.markdown(f"- **{m_name}**: `{val}` *({claim_type})*")

    with col_charts:
        st.subheader("📊 Métricas Sincronizadas de la Ronda")

        # 1. Mini Radar de Vectores en la Ronda Actual
        df_evol = get_policy_vectors_evolution(session_data)
        df_round = df_evol[df_evol["round"] == selected_round]

        if not df_round.empty:
            fig_mini_radar = go.Figure()
            dimensions_sample = POLICY_DIMENSIONS[:6] # Primeras 6 para visualización clara
            categories = [d.replace("_", " ").capitalize() for d in dimensions_sample]

            for _, row in df_round.iterrows():
                ag_id = row["agent"]
                vals = [row[dim] for dim in dimensions_sample]
                vals.append(vals[0]) # cerrar bucle

                fig_mini_radar.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=SYSTEM_LABELS.get(ag_id, ag_id),
                    line=dict(color=COLOR_PALETTE.get(ag_id, "#ECC94B"), width=2),
                    opacity=0.35,
                ))

            fig_mini_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1.0], color="#A0AEC0"),
                    bgcolor="#1A202C"
                ),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(size=10)),
                margin=dict(l=30, r=30, t=20, b=30),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
            )
            st.plotly_chart(fig_mini_radar, use_container_width=True, key="debate_room_mini_radar_chart")

        # 2. Evaluación del Árbitro en esta Ronda
        st.markdown("### ⚖️ Veredicto del Árbitro")
        if ref_eval:
            summary = ref_eval.get("summary", "Evaluación completada.")
            st.info(f"**Dictamen:** {summary}")

            rubric = ref_eval.get("rubric_scores", {})
            if rubric:
                rub_cols = st.columns(len(rubric))
                for idx, (ag, scores) in enumerate(rubric.items()):
                    if isinstance(scores, dict):
                        with rub_cols[idx]:
                            tot = scores.get("total_score", 7.5)
                            color = COLOR_PALETTE.get(ag, "#ECC94B")
                            st.metric(
                                label=f"{ag.capitalize()}",
                                value=f"{tot:.1f} / 10",
                                help=f"Rigor: {scores.get('empirical_rigor', 0)} | Coherencia: {scores.get('theoretical_coherence', 0)} | Steelman: {scores.get('steelman_score', 0)}"
                            )
        else:
            st.caption("No hay reporte específico del Árbitro para esta ronda.")
