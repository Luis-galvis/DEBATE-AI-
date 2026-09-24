"""
Vista: Recorrido Guiado (Paso a Paso).
Experiencia interactiva lineal para entender todo el experimento sin formación técnica previa.
Estructura de 11 pasos:
1. Quiénes participan (3 agentes + árbitro + simulador).
2. Reglas del juego.
3-9. Rondas 1 a 7 (con discursos compactos y Tarjeta de Cierre de cada ronda).
10. El Acuerdo Final.
11. Qué significa y qué NO significa este resultado.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any

from src.app.viz.round_summary_generator import (
    generate_round_summary_card,
    generate_full_debate_evolution_table,
    POPULAR_METRICS_CONFIG,
    get_metric_status_tag,
)
from src.app.viz.easy_charts import (
    render_explained_box,
    render_policymeter_chart,
    render_convergence_gauge,
    render_popular_metrics_cards,
    render_horizontal_comparison_bars,
)
from src.app.viz.simulation_adapter import (
    get_archetype_and_consensus_vectors,
    run_multi_position_simulations,
    compute_all_metrics_table,
)
from src.app.viz.metrics_catalog import COLOR_PALETTE, SYSTEM_LABELS

def render_guided_tour_view(session_data: Dict[str, Any], presentation_mode: bool = False):
    """Renderiza la experiencia del Recorrido Guiado paso a paso."""
    
    # Control de estado del paso actual
    if "guided_step" not in st.session_state:
        st.session_state["guided_step"] = 1
        
    total_steps = 11
    current_step = st.session_state["guided_step"]

    # Barra superior de progreso y navegación
    col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])
    
    with col_nav1:
        if st.button("⏮️ Anterior", disabled=(current_step <= 1), use_container_width=True, key="guided_tour_prev_btn"):
            st.session_state["guided_step"] = max(1, current_step - 1)
            st.rerun()
            
    with col_nav3:
        if st.button("Siguiente ⏭️", disabled=(current_step >= total_steps), use_container_width=True, type="primary", key="guided_tour_next_btn"):
            st.session_state["guided_step"] = min(total_steps, current_step + 1)
            st.rerun()

    step_titles = [
        "1. Quiénes participan",
        "2. Reglas del juego",
        "3. Ronda 1: Apertura y Tesis",
        "4. Ronda 2: Primera Simulación",
        "5. Ronda 3: Preguntas Incómodas",
        "6. Ronda 4: Choques de Crisis",
        "7. Ronda 5: Concesiones Reales",
        "8. Ronda 6: Ajuste de Parámetros",
        "9. Ronda 7: Consenso y Bautismo",
        "10. El Acuerdo Final",
        "11. Qué significa y qué NO significa"
    ]

    with col_nav2:
        progress_pct = int((current_step / total_steps) * 100)
        st.progress(progress_pct / 100.0)
        st.markdown(f"<div style='text-align: center; font-size: 0.95rem; font-weight: 700; color: #EDF2F7;'>Paso {current_step} de {total_steps}: <span style='color: #ECC94B;'>{step_titles[current_step-1]}</span></div>", unsafe_allow_html=True)

    st.markdown("---")

    # =========================================================================
    # PASO 1: QUIÉNES PARTICIPAN
    # =========================================================================
    if current_step == 1:
        st.markdown("## 👥 ¿Quiénes participan en este Consejo Económico?")
        st.markdown("**Tres inteligencias artificiales defienden posturas opuestas mientras un árbitro audita las cifras y un simulador calcula el futuro.**")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div style="background-color: #2D3748; border-top: 5px solid {COLOR_PALETTE['capitalist']}; border-radius: 8px; padding: 18px; height: 100%;">
                <h3 style="color: {COLOR_PALETTE['capitalist']}; margin-top: 0;">🔴 El Capitalista</h3>
                <p style="color: #EDF2F7; font-size: 0.94rem; line-height: 1.5;">
                    <b>Inspiración:</b> Hayek, Friedman y Schumpeter.<br><br>
                    <b>En una frase:</b> Confía en el libre mercado, la propiedad privada y los impuestos bajos como la única vía para acelerar la innovación y el crecimiento.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style="background-color: #2D3748; border-top: 5px solid {COLOR_PALETTE['collectivist']}; border-radius: 8px; padding: 18px; height: 100%;">
                <h3 style="color: {COLOR_PALETTE['collectivist']}; margin-top: 0;">🟠 El Colectivista</h3>
                <p style="color: #EDF2F7; font-size: 0.94rem; line-height: 1.5;">
                    <b>Inspiración:</b> Marx, Lange y el cooperativismo.<br><br>
                    <b>En una frase:</b> Prioriza la propiedad social, la desmercantilización de servicios básicos y la erradicación de la desigualdad de ingresos.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style="background-color: #2D3748; border-top: 5px solid {COLOR_PALETTE['socdem']}; border-radius: 8px; padding: 18px; height: 100%;">
                <h3 style="color: {COLOR_PALETTE['socdem']}; margin-top: 0;">🔵 El Socialdemócrata</h3>
                <p style="color: #EDF2F7; font-size: 0.94rem; line-height: 1.5;">
                    <b>Inspiración:</b> Keynes y el modelo nórdico.<br><br>
                    <b>En una frase:</b> Propone una economía mixta que combine la eficiencia de los mercados con un Estado de bienestar sólido y regla fiscal responsable.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_ref, col_sim = st.columns(2)
        with col_ref:
            st.markdown("""
            <div style="background-color: #1A202C; border: 1px solid #4A5568; border-left: 5px solid #ECC94B; border-radius: 8px; padding: 16px;">
                <h4 style="color: #ECC94B; margin-top: 0;">⚖️ El Árbitro-Auditor</h4>
                <p style="color: #CBD5E0; font-size: 0.92rem; margin-bottom: 0;">
                    Un juez independiente que evalúa el rigor técnico, audita cada cifra citada contra los datos de la simulación y detecta afirmaciones falsas o falacias.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_sim:
            st.markdown("""
            <div style="background-color: #1A202C; border: 1px solid #4A5568; border-left: 5px solid #3182CE; border-radius: 8px; padding: 16px;">
                <h4 style="color: #63B3ED; margin-top: 0;">⚙️ El Motor de Simulación Macroeconómica</h4>
                <p style="color: #CBD5E0; font-size: 0.92rem; margin-bottom: 0;">
                    Un modelo matemático de 30 años que calcula el impacto real de las políticas respetando la identidad contable del PIB sin sesgos políticos.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # PASO 2: REGLAS DEL JUEGO
    # =========================================================================
    elif current_step == 2:
        st.markdown("## 📜 Reglas de Oro del Debate")
        st.markdown("**Para evitar discusiones ideológicas vacías, el sistema impone cuatro reglas computacionales obligatorias:**")

        r1, r2 = st.columns(2)
        with r1:
            st.markdown("""
            <div style="background-color: #2D3748; border-radius: 8px; padding: 18px; margin-bottom: 14px; border-left: 4px solid #48BB78;">
                <b style="color: #68D391; font-size: 1.1rem;">1. Cero datos inventados (Fact-Check Estricto)</b>
                <p style="color: #E2E8F0; font-size: 0.92rem; margin-top: 6px;">
                    Ningún agente puede inventar cifras de PIB, inflación o deuda. Si citan un número que no coincide con la simulación matemática, el Árbitro les baja la puntuación automáticamente.
                </p>
            </div>
            <div style="background-color: #2D3748; border-radius: 8px; padding: 18px; border-left: 4px solid #3182CE;">
                <b style="color: #63B3ED; font-size: 1.1rem;">2. El simulador manda</b>
                <p style="color: #E2E8F0; font-size: 0.92rem; margin-top: 6px;">
                    Las buenas intenciones no bastan: si una política causa déficit fiscal o frena la inversión, las ecuaciones matemáticas reflejan las consecuencias de inmediato.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            st.markdown("""
            <div style="background-color: #2D3748; border-radius: 8px; padding: 18px; margin-bottom: 14px; border-left: 4px solid #ECC94B;">
                <b style="color: #F6E05E; font-size: 1.1rem;">3. Principio de Caridad (Steelman)</b>
                <p style="color: #E2E8F0; font-size: 0.92rem; margin-top: 6px;">
                    Antes de criticar a un rival, el agente está obligado a resumir la mejor versión posible del argumento del otro, evitando ataques fáciles o caricaturizaciones.
                </p>
            </div>
            <div style="background-color: #2D3748; border-radius: 8px; padding: 18px; border-left: 4px solid #ED8936;">
                <b style="color: #FBD38D; font-size: 1.1rem;">4. Criterio de Falsabilidad</b>
                <p style="color: #E2E8F0; font-size: 0.92rem; margin-top: 6px;">
                    Cada participante debe declarar qué dato numérico real lo obligaría a reconocer que estaba equivocado y que su rival tenía la razón.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # PASOS 3 AL 9: RONDAS 1 A 7
    # =========================================================================
    elif 3 <= current_step <= 9:
        round_idx = current_step - 2 # Ronda 1 a 7
        card = generate_round_summary_card(session_data, round_idx)
        
        st.markdown(f"## 🎙️ Ronda {round_idx}: {card['what_happened'].split('.')[0]}")
        st.markdown(f"**{card['what_happened']}**")

        # 1. Postura de cada uno en palabras simples
        st.markdown("### 💬 La postura de cada uno en esta ronda:")
        col_c, col_k, col_s = st.columns(3)
        
        with col_c:
            st_cap = card["stances"]["capitalist"]
            st.markdown(f"""
            <div style="background-color: #2D3748; border-top: 4px solid {COLOR_PALETTE['capitalist']}; border-radius: 8px; padding: 14px;">
                <b style="color: {COLOR_PALETTE['capitalist']};">🔴 El Capitalista</b><br>
                <div style="font-size: 0.88rem; color: #EDF2F7; margin-top: 6px;">
                    <b>Defiende:</b> {st_cap['defiende']}<br>
                    <b>Cedió:</b> {st_cap['cedio']}<br>
                    <b>Línea roja:</b> {st_cap['no_negocia']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_k:
            st_col = card["stances"]["collectivist"]
            st.markdown(f"""
            <div style="background-color: #2D3748; border-top: 4px solid {COLOR_PALETTE['collectivist']}; border-radius: 8px; padding: 14px;">
                <b style="color: {COLOR_PALETTE['collectivist']};">🟠 El Colectivista</b><br>
                <div style="font-size: 0.88rem; color: #EDF2F7; margin-top: 6px;">
                    <b>Defiende:</b> {st_col['defiende']}<br>
                    <b>Cedió:</b> {st_col['cedio']}<br>
                    <b>Línea roja:</b> {st_col['no_negocia']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_s:
            st_soc = card["stances"]["socdem"]
            st.markdown(f"""
            <div style="background-color: #2D3748; border-top: 4px solid {COLOR_PALETTE['socdem']}; border-radius: 8px; padding: 14px;">
                <b style="color: {COLOR_PALETTE['socdem']};">🔵 El Socialdemócrata</b><br>
                <div style="font-size: 0.88rem; color: #EDF2F7; margin-top: 6px;">
                    <b>Defiende:</b> {st_soc['defiende']}<br>
                    <b>Cedió:</b> {st_soc['cedio']}<br>
                    <b>Línea roja:</b> {st_soc['no_negocia']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Tarjeta de Cierre de la Ronda (Bloques 3, 4 y 5)
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown(f"**¿Se están poniendo de acuerdo?** ({card['convergence_pct']:.1f}% de cercanía)")
            fig_gauge = render_convergence_gauge(card["convergence_pct"])
            st.plotly_chart(fig_gauge, use_container_width=True, key=f"guided_tour_gauge_r{round_idx}")
            
            st.markdown(f"""
            <div style="font-size: 0.86rem; background-color: #1A202C; padding: 10px; border-radius: 6px; border: 1px solid #4A5568;">
                <b style="color: #68D391;">✅ En qué coinciden más:</b> {card['coinciden'][0][0]} y {card['coinciden'][1][0]}<br>
                <b style="color: #FC8181;">❌ En qué siguen chocando:</b> {card['chocan'][0][0]} y {card['chocan'][1][0]}
            </div>
            """, unsafe_allow_html=True)

        with c_right:
            st.markdown(f"**{card['consensus_status_label']}**")
            for pt in card["consensus_points"]:
                st.markdown(f"- {pt}")
            st.info(f"🔄 **Lo que cambió:** {card['what_changed']}")

        with st.expander("🔍 Ver detalle técnico y discursos completos de esta ronda", expanded=False):
            if session_data.get("rounds") and round_idx <= len(session_data["rounds"]):
                for sp in session_data["rounds"][round_idx - 1].get("speeches", []):
                    st.markdown(f"**{sp.get('speaker_name', sp.get('agent'))}:**")
                    st.text(sp.get("content", "")[:350] + "...")

    # =========================================================================
    # PASO 10: EL ACUERDO FINAL
    # =========================================================================
    elif current_step == 10:
        st.markdown("## 🏆 El Acuerdo Final de Consenso")
        st.markdown("**Tras 7 rondas de contrastación matemática y optimización evolutiva (NSGA-III), los agentes lograron converger en un punto medio viable.**")

        vectors = get_archetype_and_consensus_vectors(session_data)
        consensus_vec = vectors.get("consensus", {})

        # Regla de Posiciones
        fig_policy = render_policymeter_chart(vectors, consensus_vector=consensus_vec, show_explained_mode=True)
        st.plotly_chart(fig_policy, use_container_width=True, key="guided_tour_policymeter_step10")

        render_explained_box(
            what_shows="La posición de cada sistema (0% a 100%) en las políticas económicas clave y la estrella dorada del acuerdo.",
            how_to_read="Cada fila es una política. A la izquierda están los valores bajos y a la derecha los valores altos. La estrella dorada es el punto de consenso.",
            what_means_here="El acuerdo adoptó impuestos moderados (35%) con disciplina fiscal y gasto social focalizado, superando los extremos.",
            watch_out="Este consenso es un óptimo de compromiso; no significa que sea la única solución posible para todos los países."
        )

        st.markdown("### 📊 ¿Cómo le iría al país bajo este modelo? (6 Métricas Clave)")
        sim_res = run_multi_position_simulations(vectors, calibration_country="Colombia", scenario="baseline")
        df_metrics = compute_all_metrics_table(sim_res)
        
        # Extraer métricas del consenso
        metrics_by_system = {"capitalist": {}, "collectivist": {}, "socdem": {}, "consensus": {}}
        for item in df_metrics.to_dict(orient="records"):
            m_key = item.get("metric_key")
            for sys_id in ["capitalist", "collectivist", "socdem", "consensus"]:
                if sys_id in item and m_key:
                    metrics_by_system[sys_id][m_key] = item[sys_id]
            
        render_popular_metrics_cards(metrics_by_system)

    # =========================================================================
    # PASO 11: QUÉ SIGNIFICA Y QUÉ NO SIGNIFICA
    # =========================================================================
    elif current_step == 11:
        st.markdown("## 🎯 La Parte Honesta: Qué Significa y Qué NO Significa")
        st.markdown("**Todo modelo computacional es una simplificación de la realidad. Esta es la interpretación correcta de los resultados:**")

        col_yes, col_no = st.columns(2)
        with col_yes:
            st.markdown("""
            <div style="background-color: #2D3748; border-top: 5px solid #48BB78; border-radius: 8px; padding: 18px; height: 100%;">
                <h3 style="color: #68D391; margin-top: 0;">✅ Lo que SÍ nos enseña el modelo:</h3>
                <ul style="color: #EDF2F7; font-size: 0.92rem; line-height: 1.6; margin-bottom: 0;">
                    <li><b>Calibración con Cifras Reales:</b> El modelo toma como punto de partida la estructura de una economía emergente como Colombia (PIB per cápita inicial ~$7,500 USD anuales, desempleo ~9.8%, Gini ~0.53).</li>
                    <li><b>Proyección a 30 años:</b> En tres décadas de crecimiento continuo (2.5% a 3.5% anual), el ingreso por habitante se multiplica hasta alcanzar entre <b>$18,000 y $24,000 USD</b> anuales.</li>
                    <li><b>Convergencia Real:</b> Demuestra que inteligencias artificiales con directivas ideológicas opuestas pueden <b>ceder y converger</b> ante datos matemáticos.</li>
                    <li><b>Trade-offs Inevitables:</b> Identifica qué políticas ofrecen <b>mejores balances</b>: todo aumento de gasto exige disciplina tributaria, y todo incentivo al capital requiere cohesión social.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col_no:
            st.markdown("""
            <div style="background-color: #2D3748; border-top: 5px solid #F56565; border-radius: 8px; padding: 18px; height: 100%;">
                <h3 style="color: #FC8181; margin-top: 0;">❌ Lo que NO debemos asumir:</h3>
                <ul style="color: #EDF2F7; font-size: 0.92rem; line-height: 1.6; margin-bottom: 0;">
                    <li><b>No es una receta mágica ni dogma:</b> Cada nación tiene realidades institucionales, informales y geográficas distintas.</li>
                    <li><b>No reemplaza la soberanía democrática:</b> Los algoritmos calculan curvas de frontera eficiente, pero las prioridades de gasto y valores morales pertenecen a la ciudadanía.</li>
                    <li><b>Límites del simulador:</b> Es un modelo macroeconómico continuo; no incluye especulación financiera a corto plazo ni shocks geopolíticos bélicos impredecibles.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **Próximo paso:** Explora la pestaña **'🏆 2. Resultado Final'** para ver la ficha detallada del pacto, o entra en **'🔬 3. Explorar (Avanzado)'** para probar los simuladores de choques de crisis y mover los sliders de tus prioridades.")
