"""
Dashboard Interactivo en Streamlit: Consejo Económico de IA.
Visualizador Gráfico del Debate, Simulación Macroeconómica Continua,
Convergencia de Posiciones, Tablero Integral de Métricas y Consenso Final.
Optimizado para alta legibilidad en 1080p y 4K con Modo Presentación.
"""

import os
import sys
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config import OUTPUTS_DIR, RANDOM_SEED
from src.simulation.policy_vector import (
    PolicyVector,
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)
from src.simulation.solow_engine import MacroEconomy
from src.simulation.shocks import ALL_SCENARIOS
from src.simulation.metrics import calculate_metrics
from src.agents.orchestrator import DebateOrchestrator
from src.reporting.report_generator import SynthesisReportGenerator
from src.reporting.video_assets import generate_key_moments_doc, generate_video_script_doc, export_video_charts

# Importar adaptadores y vistas del nuevo módulo
from src.app.viz.debate_adapter import load_debate_session_data, _normalize_session_data
from src.app.viz.simulation_adapter import (
    get_archetype_and_consensus_vectors,
    run_multi_position_simulations,
    compute_all_metrics_table,
    compute_shock_resilience_comparison,
)
from src.app.viz.findings_generator import generate_automated_findings
from src.app.viz.export_helper import create_video_assets_zip

from src.app.views.view_debate_room import render_debate_room_view
from src.app.views.view_positions import render_positions_convergence_view
from src.app.views.view_metrics_board import render_metrics_board_view
from src.app.views.view_consensus import render_consensus_profile_view
from src.app.views.view_custom_priorities import render_custom_priorities_view
from src.app.views.view_debate_rigor import render_debate_rigor_view
from src.app.views.view_glossary import render_glossary_view

# Configuración de página
st.set_page_config(
    page_title="Consejo Económico de IA | Visualizador Gráfico & Consenso",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS optimizados para 1080p, 4K y accesibilidad
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .main-header {
        font-family: 'Outfit', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3182CE, #805AD5, #D69E2E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .disclaimer-box {
        background-color: #2D3748;
        border-left: 5px solid #ECC94B;
        padding: 12px 18px;
        border-radius: 6px;
        margin-bottom: 14px;
        font-size: 0.92rem;
        color: #F7FAFC;
        line-height: 1.5;
    }
    .welcome-box {
        background-color: rgba(49, 130, 206, 0.12);
        border: 1px solid #3182CE;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 18px;
    }
    .finding-card {
        background-color: #2D3748;
        border: 1px solid #4A5568;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .finding-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F6E05E;
        margin-bottom: 6px;
    }
    .finding-insight {
        font-size: 0.93rem;
        line-height: 1.55;
        color: #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Principal
st.markdown('<div class="main-header">🏛️ Consejo Económico de IA</div>', unsafe_allow_html=True)
st.markdown("**Debate Multi-Agente con Simulación Macroeconómica Determinista y Optimización de Pareto (NSGA-III)**")

# Banner Permanente de Advertencia Educativa
st.markdown("""
<div class="disclaimer-box">
    ⚠️ <b>AVISO PEDAGÓGICO Y DE DIVULGACIÓN:</b> Este sistema constituye un modelo computacional simplificado con fines educativos y de divulgación sobre economía cuantitativa, datos e ingeniería de software. Las simulaciones y el modelo de consenso sintetizado no constituyen asesoría ni recomendaciones directas de política pública para ninguna jurisdicción real.
</div>
""", unsafe_allow_html=True)

# Pantalla de Bienvenida: "Cómo leer este tablero en 60 segundos"
with st.expander("💡 ¿Cómo leer este tablero en 60 segundos? (Guía Rápida para Principiantes)", expanded=False):
    st.markdown("""
    <div class="welcome-box">
        <ol style="margin-bottom: 0; line-height: 1.6; color: #EDF2F7;">
            <li><b>Cada posición es un 'paquete de políticas':</b> Los 3 agentes defienden visiones coherentes basadas en escuelas reales (Hayek vs Marx vs Keynes).</li>
            <li><b>Simulación matemática continua:</b> El motor calcula 30 años de evolución respetando la identidad contable exacta (Producción = Consumo + Inversión + Gasto + Exportaciones Netas).</li>
            <li><b>Rangos de probabilidad, no profecías:</b> Las trayectorias muestran bandas de incertidumbre ante 7 escenarios de crisis macroeconómicas.</li>
            <li><b>No hay un ganador único:</b> Todo avance en crecimiento tiene costos distributivos, y todo aumento de gasto exige disciplina fiscal.</li>
            <li><b>El Consenso es un compromiso óptimo:</b> Se sintetizó con algoritmos de optimización para maximizar el bienestar social sin comprometer la solvencia del país.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# BARRA LATERAL: CONTROLES DE SESIÓN Y MODO PRESENTACIÓN
# =============================================================================
st.sidebar.title("⚙️ Control de Sesión")
presentation_mode = st.sidebar.toggle(
    "🎬 Modo Presentación (Video)",
    value=False,
    key="sidebar_presentation_toggle",
    help="Oculta paneles técnicos y destaca gráficos clave para grabación limpia en 1080p/4K."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Nivel de Explicación")
reading_level_choice = st.sidebar.radio(
    "Modalidad Pedagógica",
    ["simple", "intermedio", "tecnico"],
    key="sidebar_reading_level_radio",
    format_func=lambda x: {
        "simple": "🌱 Simple (Público General)",
        "intermedio": "⚖️ Intermedio (Técnico + Popular)",
        "tecnico": "🔬 Técnico Avanzado (Matemáticas)"
    }[x],
    index=0,
    help="Cambia el nivel de jerga y detalle de las explicaciones en todas las vistas."
)
st.session_state["reading_level"] = reading_level_choice

st.sidebar.markdown("---")
calib_choice = st.sidebar.selectbox(
    "País de Calibración",
    ["colombia", "nordic", "usa"],
    key="sidebar_calib_choice_select",
    format_func=lambda x: {"colombia": "🇨🇴 Colombia (Emergente Media)", "nordic": "🇸🇪 Suecia (Nórdica Avanzada)", "usa": "🇺🇸 Estados Unidos"}[x]
)

from src.config import is_groq_configured

is_hosted_demo = os.getenv("HOSTED_REPLAY_ONLY", "false").lower() == "true"

if is_hosted_demo or not is_groq_configured():
    mode_choice = "replay"
    st.sidebar.info("🔒 **Modo Replay Verificado Activo** (0 tokens / Reproducción instantánea). Si descargas el código en GitHub puedes configurar tu `GROQ_API_KEY` para ejecutar en vivo.")
else:
    mode_choice = st.sidebar.radio(
        "Modo de Ejecución LLM (Groq)",
        ["replay", "record", "live"],
        index=0,
        key="sidebar_mode_choice_radio",
        help="replay: Reproduce instantáneamente desde caché local offline (0 tokens); record: Llama a Groq y guarda en caché; live: Llama a Groq en vivo."
    )

if st.sidebar.button("🚀 Ejecutar Nuevo Debate (7 Rondas)", type="primary", key="sidebar_run_debate_btn"):
    with st.spinner("Ejecutando simulación macro, debate de agentes y optimización NSGA-III..."):
        effective_mode = "replay" if (is_hosted_demo or (mode_choice != "replay" and not is_groq_configured())) else mode_choice
        orchestrator = DebateOrchestrator(calibration_country=calib_choice, execution_mode=effective_mode)
        session_data = orchestrator.run_all_rounds()
        st.session_state["latest_session"] = session_data

        if orchestrator.synthesis_proposal and orchestrator.synthesis_result:
            rep_gen = SynthesisReportGenerator(
                proposal=orchestrator.synthesis_proposal,
                synthesis_data=orchestrator.synthesis_result,
                calibration_country=calib_choice.capitalize()
            )
            rep_gen.export_markdown_file()
            try:
                rep_gen.export_pdf_file()
            except Exception as pdf_err:
                st.sidebar.warning(f"Aviso PDF: {pdf_err}")

            generate_key_moments_doc(session_data)
            generate_video_script_doc()
            export_video_charts()

        st.sidebar.success("✅ ¡Debate completado y sintetizado con éxito!")

# Cargar datos de la sesión (en memoria o desde disco)
if "latest_session" in st.session_state:
    session_data = _normalize_session_data(st.session_state["latest_session"])
else:
    session_data = load_debate_session_data()

from src.app.views.view_guided_tour import render_guided_tour_view
from src.app.views.view_chart_guide import render_chart_guide_view
from src.app.views.view_interview import render_interview_view

# =============================================================================
# PESTAÑAS PRINCIPALES DEL VISUALIZADOR (5 SECCIONES ESTRUCTURADAS)
# =============================================================================
main_tabs = st.tabs([
    "🧭 1. Recorrido Guiado",
    "🏆 2. Resultado Final",
    "💬 3. Hablar con las IAs (Entrevista)",
    "🔬 4. Explorar (Avanzado)",
    "📖 5. Glosario & Guía Gráfica",
])

# -----------------------------------------------------------------------------
# 1. RECORRIDO GUIADO (Modo Fácil por Defecto)
# -----------------------------------------------------------------------------
with main_tabs[0]:
    render_guided_tour_view(session_data, presentation_mode=presentation_mode)

# -----------------------------------------------------------------------------
# 2. RESULTADO FINAL (Ficha del Consenso y Policymeter)
# -----------------------------------------------------------------------------
with main_tabs[1]:
    render_consensus_profile_view(session_data, presentation_mode=presentation_mode)

# -----------------------------------------------------------------------------
# 3. HABLAR CON LAS IAS (Entrevista Directa e Interrogatorio)
# -----------------------------------------------------------------------------
with main_tabs[2]:
    render_interview_view(session_data, presentation_mode=presentation_mode)

# -----------------------------------------------------------------------------
# 4. EXPLORAR (Vistas Técnicas, Simuladores y Auditoría)
# -----------------------------------------------------------------------------
with main_tabs[3]:
    explore_tabs = st.tabs([
        "🎙️ Sala de Debate (7 Rondas)",
        "🗺️ Mapa & Convergencia",
        "📊 Tablero Integral de Métricas",
        "🎛️ Sliders de Prioridades",
        "🔍 Rigor & Auditoría de Cifras",
        "💡 Hallazgos Automáticos",
        "📦 Centro de Exportación Video",
    ])
    
    # 3.1 Sala de debate
    with explore_tabs[0]:
        render_debate_room_view(session_data, presentation_mode=presentation_mode)
        
    # 3.2 Mapa de posiciones
    with explore_tabs[1]:
        render_positions_convergence_view(session_data, presentation_mode=presentation_mode)
        
    # 3.3 Tablero de métricas
    with explore_tabs[2]:
        render_metrics_board_view(session_data, presentation_mode=presentation_mode)
        
    # 3.4 Sliders de prioridades
    with explore_tabs[3]:
        render_custom_priorities_view(session_data, presentation_mode=presentation_mode)
        
    # 3.5 Rigor del debate
    with explore_tabs[4]:
        render_debate_rigor_view(session_data, presentation_mode=presentation_mode)
        
    # 3.6 Hallazgos automáticos
    with explore_tabs[5]:
        st.header("💡 Hallazgos Analíticos Automáticos (Calculados por Código)")
        st.markdown("Observaciones cuantitativas deterministas derivadas de las 30 simulaciones anuales y las 7 rondas de debate.")

        vectors = get_archetype_and_consensus_vectors(session_data)
        sim_res = run_multi_position_simulations(vectors, calibration_country="Colombia", scenario="baseline")
        df_metrics = compute_all_metrics_table(sim_res)
        df_resilience = compute_shock_resilience_comparison(vectors, calibration_country="Colombia")
        findings = generate_automated_findings(df_metrics, session_data, df_resilience)

        for fd in findings:
            st.markdown(f"""
            <div class="finding-card">
                <div class="finding-title">{fd['title']} <span style="font-size: 0.8rem; background-color: #1A202C; padding: 2px 8px; border-radius: 4px; border: 1px solid #4A5568; margin-left: 8px;">{fd['category']}</span></div>
                <div class="finding-insight">{fd['insight']}</div>
                <div style="font-size: 0.82rem; color: #A0AEC0; margin-top: 8px;">📍 Gráfico respaldatorio: <b>{fd['target_view']}</b></div>
            </div>
            """, unsafe_allow_html=True)

    # 3.7 Centro de exportación
    with explore_tabs[6]:
        st.header("📦 Centro de Recursos para Video y Descargas")
        st.markdown("Descarga los informes técnicos ejecutivos, el guion de video y el paquete completo de figuras en alta resolución (PNG 300 DPI y SVG).")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.subheader("📄 Documentos e Informes")
            pdf_path = OUTPUTS_DIR / "final_synthesis_report.pdf"
            if pdf_path.exists():
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Descargar Informe Final (PDF Ejecutivo)",
                        data=f.read(),
                        file_name="Consejo_Economico_IA_Informe_Final.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

            md_path = OUTPUTS_DIR / "final_synthesis_report.md"
            if md_path.exists():
                with open(md_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        label="📥 Descargar Informe Final (Markdown)",
                        data=f.read(),
                        file_name="Consejo_Economico_IA_Informe_Final.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

            script_candidates = [
                OUTPUTS_DIR / "GUION_VIDEO.md",
                ROOT_DIR / "docs" / "video" / "GUION_VIDEO.md",
                OUTPUTS_DIR / "video_script.md",
            ]
            script_path = next((p for p in script_candidates if p.exists()), None)
            if script_path:
                with open(script_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        label="🎬 Descargar Guion Técnico de Video (Markdown)",
                        data=f.read(),
                        file_name="guion_video_divulgacion.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

        with col_d2:
            st.subheader("🖼️ Paquete de Figuras y Gráficos (ZIP)")
            st.markdown("Incluye todas las gráficas generadas en formato vectorial SVG y PNG 300 DPI listas para edición de video.")

            zip_bytes = create_video_assets_zip()
            st.download_button(
                label="📦 Descargar Paquete Completo de Gráficos (ZIP)",
                data=zip_bytes,
                file_name="recursos_graficos_video.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True
            )

# -----------------------------------------------------------------------------
# 5. GLOSARIO & GUÍA GRÁFICA
# -----------------------------------------------------------------------------
with main_tabs[4]:
    guide_tabs = st.tabs([
        "📖 Glosario Económico",
        "📊 ¿Cómo leer los gráficos de este proyecto?",
    ])
    with guide_tabs[0]:
        render_glossary_view(session_data, presentation_mode=presentation_mode)
    with guide_tabs[1]:
        render_chart_guide_view(presentation_mode=presentation_mode)

