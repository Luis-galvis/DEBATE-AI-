"""
Vista D / Tab 2: Resultado Final (Ficha del Consenso, Veredicto Autónomo del Árbitro, Policymeter y Métricas Clave).
Diseño en Modo Fácil por defecto con panel desplegable para detalle técnico avanzado y descarga de reporte PDF.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path

from src.app.viz.simulation_adapter import (
    get_archetype_and_consensus_vectors,
    run_multi_position_simulations,
    compute_all_metrics_table,
)
from src.app.viz.metrics_catalog import COLOR_PALETTE, SYSTEM_LABELS
from src.app.viz.easy_charts import (
    render_policymeter_chart,
    render_popular_metrics_cards,
    render_explained_box,
    render_horizontal_comparison_bars,
)
from src.optimization.pareto_optimizer import run_pareto_optimization
from src.reporting.report_generator import SynthesisReportGenerator
from src.agents.schemas import SynthesisModelProposal, PolicyVectorSchema, RefereeAutonomousVerdict
from src.config import OUTPUTS_DIR

@st.cache_data(show_spinner="Calculando frontera de Pareto...")
def get_cached_pareto_results(country: str = "colombia", n_gen: int = 15, pop_size: int = 20, seed: int = 42) -> dict:
    return run_pareto_optimization(
        calibration_country=country,
        n_gen=n_gen,
        pop_size=pop_size,
        random_seed=seed,
    )

def render_consensus_profile_view(session_data: dict, presentation_mode: bool = False):
    """Renderiza la Vista del Resultado Final de Consenso y el Dictamen del Árbitro."""
    st.header("🏆 Resultado Final: El Modelo de Consenso y Dictamen Arbitral")
    st.markdown("La síntesis alcanzada tras 7 rondas de debate y optimización multiobjetivo (NSGA-III), acompañada del veredicto técnico autónomo del Árbitro.")

    vectors = get_archetype_and_consensus_vectors(session_data)
    cons_vec = vectors["consensus"]
    proposal_dict = session_data.get("proposal", {})
    model_name = proposal_dict.get("model_name", "Modelo de Innovación Competitiva, Flexiseguridad y Cohesión Productiva (ICF-CP)")
    tagline = proposal_dict.get("tagline", "Mercados dinámicos con disciplina de precios, flexiseguridad laboral y un Estado de Bienestar con ancla fiscal intertemporal.")

    # 1. Ficha de Identidad Destacada del Modelo de Consenso
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(214, 158, 46, 0.22), rgba(49, 130, 206, 0.22)); border: 2px solid #D69E2E; padding: 22px 26px; border-radius: 12px; margin-bottom: 24px;">
        <div style="font-size: 1.65rem; font-weight: 800; color: #F6E05E; margin-bottom: 6px;">
            🏛️ {model_name}
        </div>
        <div style="font-size: 1.05rem; font-style: italic; color: #EDF2F7; margin-bottom: 12px;">
            "{tagline}"
        </div>
        <div style="font-size: 0.94rem; line-height: 1.6; color: #CBD5E0;">
            <b>Pacto de Compromiso (Pareto-Eficiente):</b> Integra la asignación descentralizada de precios y el dinamismo innovador del sector privado con un piso de protección social universal (salud y educación) financiado con tributación progresiva y anclado en una regla fiscal anticíclica estricta.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Veredicto y Dictamen Autónomo del Árbitro
    st.markdown("### ⚖️ Veredicto Autónomo e Independiente del Árbitro-Auditor")
    st.markdown("""
    > *El Árbitro evalúa de forma independiente los tres marcos teóricos puros (Capitalismo de Libre Mercado, Comunismo Colectivista y Socialdemocracia Nórdica) para dictaminar cuál es el modelo más eficiente y beneficioso para **todos los sectores de la población**, sin estar condicionado por las concesiones del debate.*
    """)

    verdict_dict = session_data.get("autonomous_verdict") or {}
    chosen_model = verdict_dict.get("chosen_model", "Socialdemocracia Nórdica / Economía Social de Mercado con Flexiseguridad")
    
    st.markdown(f"""
    <div style="background-color: #2D3748; border-left: 6px solid #48BB78; padding: 16px 20px; border-radius: 8px; margin-bottom: 18px;">
        <div style="font-size: 1.15rem; font-weight: 700; color: #68D391; margin-bottom: 6px;">
            👑 Modelo Elegido por el Árbitro: {chosen_model}
        </div>
        <div style="font-size: 0.93rem; color: #E2E8F0; line-height: 1.55;">
            <b>Fundamento Técnico:</b> En la evaluación intertemporal y bajo choques de estrés macroeconómico (pandemias y recesiones), la economía mixta con flexiseguridad optimiza simultáneamente la acumulación de capital humano, el crecimiento de la Productividad Total de los Factores (TFP) y la cohesión social, superando las fallas de los dos extremos.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Explicación pedagógica de por qué fallan Hayek y Marx
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("""
        <div style="background-color: #1A202C; border: 1px solid #E53E3E; border-radius: 8px; padding: 14px 18px; height: 100%;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #FC8181; margin-bottom: 8px;">
                ❌ ¿Por qué falla el Capitalismo Puro de Hayek / Friedman?
            </div>
            <ul style="font-size: 0.88rem; color: #E2E8F0; line-height: 1.5; padding-left: 18px; margin: 0;">
                <li><b>Desigualdad estructural persistente (Gini > 0.48):</b> Sin transferencias ni bienes públicos universales, la riqueza se concentra y perpetúa la pobreza intergeneracional.</li>
                <li><b>Subinversión en Capital Humano:</b> Los quintiles más vulnerables (Q1-Q2) no pueden autofinanciar salud y educación de calidad, frenando el potencial de la TFP.</li>
                <li><b>Fallas de Mercado y Externalidades:</b> Incapacidad para internalizar el daño ambiental (emisiones de CO2) y asimetrías de información sin regulación.</li>
                <li><b>Extrema Fragilidad ante Choques:</b> En crisis sanitarias o financieras, la falta de una red de seguridad dispara el desempleo y el colapso de la demanda interna.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_v2:
        st.markdown("""
        <div style="background-color: #1A202C; border: 1px solid #DD6B20; border-radius: 8px; padding: 14px 18px; height: 100%;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #F6AD55; margin-bottom: 8px;">
                ❌ ¿Por qué falla el Comunismo / Colectivismo Puro de Marx?
            </div>
            <ul style="font-size: 0.88rem; color: #E2E8F0; line-height: 1.5; padding-left: 18px; margin: 0;">
                <li><b>Problema del Cálculo Económico (Mises-Hayek):</b> Al abolir el sistema de precios de mercado libre, el planificador central es incapaz de conocer la escasez relativa de bienes.</li>
                <li><b>Destrucción de Incentivos y TFP:</b> La ausencia de premios al riesgo, la innovación y el esfuerzo individual causa estancamiento tecnológico y productividad negativa.</li>
                <li><b>Burocratización y Captura:</b> Concentración masiva del poder económico en el aparato estatal, generando ineficiencias de asignación y corrupción.</li>
                <li><b>Déficit Crónico e Inflación:</b> El financiamiento de subsidios universales sin respaldo productivo dispara la deuda sobre el PIB (>88%) y la inflación.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Beneficio para los 4 sectores de la sociedad
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 👥 Impacto y Beneficio para Todos los Sectores de la Población")
    c_s1, c_s2, c_s3, c_s4 = st.columns(4)
    with c_s1:
        st.markdown("""
        <div style="background-color: #2D3748; border: 1px solid #4A5568; border-radius: 8px; padding: 12px 14px; min-height: 160px;">
            <div style="font-weight: 700; color: #63B3ED; margin-bottom: 4px;">👶 Familias Vulnerables (Q1-Q2)</div>
            <div style="font-size: 0.84rem; color: #CBD5E0; line-height: 1.45;">
                Piso de protección universal con salud y educación gratuitas de alta calidad, y transferencias directas que erradican la pobreza extrema.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c_s2:
        st.markdown("""
        <div style="background-color: #2D3748; border: 1px solid #4A5568; border-radius: 8px; padding: 12px 14px; min-height: 160px;">
            <div style="font-weight: 700; color: #F6E05E; margin-bottom: 4px;">👷 Clase Media (Q3-Q4)</div>
            <div style="font-size: 0.84rem; color: #CBD5E0; line-height: 1.45;">
                Flexiseguridad: seguro de desempleo robusto y reentrenamiento digital continuo, garantizando estabilidad ante la automatización laboral.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c_s3:
        st.markdown("""
        <div style="background-color: #2D3748; border: 1px solid #4A5568; border-radius: 8px; padding: 12px 14px; min-height: 160px;">
            <div style="font-weight: 700; color: #68D391; margin-bottom: 4px;">💼 Empresarios e Inversores (Q5)</div>
            <div style="font-size: 0.84rem; color: #CBD5E0; line-height: 1.45;">
                Precios libres, seguridad jurídica, apertura comercial, baja burocracia y acceso a una fuerza laboral sana y altamente calificada.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c_s4:
        st.markdown("""
        <div style="background-color: #2D3748; border: 1px solid #4A5568; border-radius: 8px; padding: 12px 14px; min-height: 160px;">
            <div style="font-weight: 700; color: #B794F4; margin-bottom: 4px;">🏛️ El Estado y Finanzas</div>
            <div style="font-size: 0.84rem; color: #CBD5E0; line-height: 1.45;">
                Recaudo tributario sólido (~34% PIB) con regla fiscal estructural anticíclica que reduce la deuda soberana y asegura solvencia intertemporal.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Regla de Posiciones (Policymeter)
    st.subheader("📏 Regla de Posiciones de Política Pública (Policymeter)")
    fig_policy = render_policymeter_chart(vectors, consensus_vector=cons_vec.to_dict(), show_explained_mode=True)
    st.plotly_chart(fig_policy, use_container_width=True, key="consensus_view_policymeter")

    render_explained_box(
        what_shows="Ubicación exacta del modelo de consenso (estrella dorada) respecto a las tres posturas iniciales (rojo, naranja, azul).",
        how_to_read="Cada fila representa una política pública de 0% a 100%. Los extremos representan las posturas radicales y el centro representa zonas de compromiso.",
        what_means_here="El acuerdo fijó impuestos moderados-progresivos (42%), recaudo robusto (34% PIB), gasto social del 38% y propiedad pública estratégica del 20%, evitando extremos destructivos.",
        watch_out="Este consenso es un óptimo matemático Pareto-eficiente que maximiza el bienestar social general."
    )

    # 4. Métricas Clave de Simulación
    st.subheader("📊 Indicadores Macroeconómicos y Fiscales Clave")
    sim_res = run_multi_position_simulations(vectors, calibration_country="Colombia", scenario="baseline")
    df_metrics = compute_all_metrics_table(sim_res)

    metrics_by_system = {"capitalist": {}, "collectivist": {}, "socdem": {}, "consensus": {}}
    for item in df_metrics.to_dict(orient="records"):
        m_key = item.get("metric_key")
        for sys_id in ["capitalist", "collectivist", "socdem", "consensus"]:
            if sys_id in item and m_key:
                metrics_by_system[sys_id][m_key] = item[sys_id]

    render_popular_metrics_cards(metrics_by_system)

    # 5. Comparativa de Barras Simples
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        fig_gdp = render_horizontal_comparison_bars(df_metrics, "terminal_gdp_pc", "Crecimiento Económico (PIB pc en 30 años)")
        st.plotly_chart(fig_gdp, use_container_width=True, key="consensus_view_gdp_bars")
    with col_b2:
        fig_gini = render_horizontal_comparison_bars(df_metrics, "gini_avg", "Igualdad de Ingresos (Gini: menor es más parejo)")
        st.plotly_chart(fig_gini, use_container_width=True, key="consensus_view_gini_bars")

    # 6. Botón de Descarga del Reporte Técnico Oficial en PDF
    st.markdown("---")
    st.subheader("📄 Exportar Reporte Técnico Oficial en PDF")
    st.markdown("Descarga el documento formal completo con el veredicto del árbitro, análisis teórico detallado, tablas de políticas y métricas de simulación.")

    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        if st.button("🔄 Generar / Actualizar Reporte Técnico Oficial (PDF)", key="gen_pdf_btn", use_container_width=True):
            with st.spinner("Compilando reporte formal con ReportLab..."):
                prop_obj = SynthesisModelProposal(
                    model_name=model_name,
                    tagline=tagline,
                    core_principles=proposal_dict.get("core_principles", [
                        "Precios descentralizados e incentivos de mercado para I+D y productividad.",
                        "Red de seguridad universal y flexiseguridad laboral para proteger al trabajador.",
                        "Regla fiscal estructural y banco central autónomo.",
                    ]),
                    inherited_from_capitalist=proposal_dict.get("inherited_from_capitalist", ["Mecanismo de precios libres", "Apertura comercial"]),
                    inherited_from_collectivist=proposal_dict.get("inherited_from_collectivist", ["Salud y educación universales", "Impuestos sobre rentas monopólicas"]),
                    inherited_from_socdem=proposal_dict.get("inherited_from_socdem", ["Flexiseguridad", "Regla fiscal anticíclica"]),
                    policy_vector=PolicyVectorSchema.from_array(cons_vec.values),
                )
                
                # Consolidar métricas para el reporte
                cons_metrics = metrics_by_system.get("consensus", {})
                rep_data = {
                    "synthesized_metrics": cons_metrics,
                    "autonomous_verdict": verdict_dict,
                }
                
                rep_gen = SynthesisReportGenerator(
                    proposal=prop_obj,
                    synthesis_data=rep_data,
                    calibration_country="Colombia",
                    autonomous_verdict=verdict_dict,
                )
                pdf_path = rep_gen.export_pdf_file()
                md_path = rep_gen.export_markdown_file()
                st.success(f"¡Reporte PDF generado exitosamente en `{pdf_path.name}`!")

    with col_p2:
        pdf_file_path = OUTPUTS_DIR / "final_synthesis_report.pdf"
        if pdf_file_path.exists():
            with open(pdf_file_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="📥 Descargar Reporte Completo (PDF)",
                data=pdf_bytes,
                file_name="reporte_consejo_economico_ia.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf_btn",
            )

    # 7. Detalle Técnico Avanzado (Cerrado por defecto)
    with st.expander("🔬 Ver Detalle Técnico Avanzado (Frontera de Pareto 2D/3D, Gráfico Ternario y Valores Exactos)", expanded=False):
        st.markdown("### Tabla Completa de Parámetros de Política (10 Dimensiones)")
        st.dataframe(pd.DataFrame([cons_vec.to_dict()]), use_container_width=True)

        st.markdown("### Frontera de Pareto y Trade-Offs (NSGA-III)")
        opt_res = get_cached_pareto_results()
        if "pareto_F_natural" in opt_res:
            F_nat = opt_res["pareto_F_natural"]
            cols = ["PIB_pc", "Gini", "Deuda_PIB", "Resiliencia", "Bienestar"]
            if hasattr(F_nat, "shape") and F_nat.shape[1] == len(cols):
                df_pareto = pd.DataFrame(F_nat, columns=cols)
            else:
                df_pareto = pd.DataFrame(F_nat)
                for i, col_name in enumerate(cols[:df_pareto.shape[1]]):
                    df_pareto.rename(columns={i: col_name}, inplace=True)

            if "Gini" in df_pareto.columns and "PIB_pc" in df_pareto.columns:
                fig_p2d = px.scatter(
                    df_pareto,
                    x="Gini",
                    y="PIB_pc",
                    color="Bienestar" if "Bienestar" in df_pareto.columns else None,
                    title="Frontera de Pareto: Crecimiento vs Igualdad de Ingresos",
                    labels={"Gini": "Desigualdad (Gini)", "PIB_pc": "PIB per cápita (USD)"},
                    template="plotly_dark",
                )
                fig_p2d.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(26, 32, 44, 0.6)", height=380)
                st.plotly_chart(fig_p2d, use_container_width=True, key="consensus_view_pareto_scatter")

