"""
Vista: Glosario Económico Interactivo y Pedagógico (view_glossary.py).
Permite buscar y explorar todas las métricas, parámetros y conceptos del modelo en lenguaje accesible.
"""

import streamlit as st
import pandas as pd
from src.app.viz.glossary_loader import get_glossary, format_help_card

def render_glossary_view(session_data: dict, presentation_mode: bool = False):
    """Renderiza la Vista del Glosario Económico."""
    st.header("📖 Glosario Económico en Lenguaje Cotidiano")
    st.markdown("Consulta qué significa cada término, cómo interpretarlo, su analogía de la vida diaria y lo que NO mide.")

    glossary = get_glossary()
    categories = glossary.get_categories()

    col_search, col_cat = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Buscar término o concepto:", placeholder="Ej: Gini, Deuda, Inflación, Consenso, Pareto...", key="glossary_search")

    with col_cat:
        selected_category = st.selectbox("Filtrar por Categoría:", categories, key="glossary_cat_filter")

    # Filtrar entradas
    entries = glossary.get_all(selected_category)
    if search_query:
        q = search_query.lower().strip()
        entries = [
            e for e in entries
            if q in e.nombre_simple.lower()
            or q in e.nombre_tecnico.lower()
            or q in e.definicion_corta.lower()
            or any(q in s.lower() for s in e.sinonimos)
        ]

    st.markdown(f"**Términos encontrados:** `{len(entries)}`")
    st.markdown("---")

    if not entries:
        st.info("No se encontraron términos que coincidan con la búsqueda.")
        return

    # Renderizar tarjetas
    for entry in entries:
        with st.expander(f"📌 {entry.nombre_simple} — *({entry.nombre_tecnico})*", expanded=(len(entries) <= 3)):
            st.markdown(f"""
            <div style="background-color: #2D3748; padding: 16px 20px; border-radius: 8px; border-left: 5px solid #3182CE; margin-bottom: 8px;">
                <div style="font-size: 1.05rem; font-weight: 700; color: #F6E05E; margin-bottom: 6px;">
                    {entry.nombre_simple} <span style="font-size: 0.82rem; font-weight: normal; color: #A0AEC0;">[{entry.categoria}]</span>
                </div>
                <div style="font-size: 0.95rem; color: #EDF2F7; margin-bottom: 12px; line-height: 1.5;">
                    💡 <b>En una frase:</b> {entry.definicion_corta}
                </div>
                <div style="font-size: 0.92rem; color: #CBD5E0; line-height: 1.5; margin-bottom: 8px;">
                    🍕 <b>Analogía cotidiana:</b> {entry.analogia_cotidiana}
                </div>
                <div style="font-size: 0.92rem; color: #CBD5E0; line-height: 1.5; margin-bottom: 8px;">
                    🧭 <b>Cómo interpretarlo:</b> {entry.como_leerlo}
                </div>
                <div style="font-size: 0.92rem; color: #CBD5E0; line-height: 1.5; margin-bottom: 8px;">
                    🌟 <b>Por qué importa:</b> {entry.por_que_importa}
                </div>
                <div style="font-size: 0.92rem; color: #FEB2B2; line-height: 1.5; margin-bottom: 8px;">
                    ⚠️ <b>Lo que NO mide:</b> {entry.lo_que_no_mide}
                </div>
            </div>
            """, unsafe_allow_html=True)
