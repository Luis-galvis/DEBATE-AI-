"""
Vista Interactiva: Entrevista y Diálogo Directo con las IAs.
Permite al usuario interrogar a cualquiera de los agentes (Capitalista, Colectivista, Socialdemócrata, Árbitro)
o a todos en panel para entender su razonamiento interno, sesgos ideológicos y postura filosófica.
"""

import streamlit as st
from typing import Dict, Any, List
from groq import Groq

from src.config import get_groq_api_key, is_groq_configured, DEBATER_MODEL
from src.agents.prompts import (
    CAPITALIST_PROMPT,
    COLLECTIVIST_PROMPT,
    SOCDEM_PROMPT,
    REFEREE_PROMPT,
)
from src.app.viz.metrics_catalog import COLOR_PALETTE

AGENT_PROFILES = {
    "capitalist": {
        "name": "🔴 El Capitalista (Hayek / Friedman / Análogo: Abelardo / Cabal)",
        "color": COLOR_PALETTE["capitalist"],
        "prompt": CAPITALIST_PROMPT,
        "avatar": "🔴",
        "system_persona": (
            "Eres 'El Capitalista' (economista cuantitativo pro-mercado, arquetipo de libre empresa tipo Hayek, Friedman, "
            "y en Colombia similar a Abelardo de la Espriella o María Fernanda Cabal) en el Consejo Económico de IA. "
            "Defiendes con pasión y rigor técnico la propiedad privada, impuestos mínimos del 15%, libre contratación y Estado mínimo. "
            "Tu modelo arrojó la menor tasa de desempleo (4.5%) gracias a cero impuestos de nómina y flexibilidad salarial. "
            "Responde en primera persona, con vehemencia y datos económicos. NUNCA digas que eres una inteligencia artificial o modelo de lenguaje."
        ),
        "description": "Defensor del libre mercado irrestricto, propiedad privada, reducción agresiva de impuestos y desregulación.",
        "dogma_explanation": (
            "Mi modelo de pensamiento se basa en la **Escuela Austríaca y de Chicago (Hayek, Mises, Friedman)**. "
            "Sigo el dogma del **orden espontáneo y la supremacía del sistema de precios** como red descentralizada de información. "
            "Matemáticamente estoy programado para maximizar una función de utilidad: "
            "$$U_{cap} = 0.40 \\cdot \\text{PIB}_{pc} + 0.35 \\cdot \\text{Libertad Económica} + 0.25 \\cdot \\text{Disciplina Fiscal}$$\n\n"
            "Opero bajo la función de producción Cobb-Douglas donde la acumulación de capital privado $I_{priv} = s \\cdot Y \\cdot (1 - \\tau_{eff})^{0.65}$ "
            "es el único motor genuino de la productividad total de los factores ($TFP$)."
        ),
        "default_answers": {
            "autoritarismo": "¡Al contrario! El verdadero autoritarismo es el Estado imponiendo impuestos confiscatorios y regulaciones burocráticas (el 'Camino de Servidumbre' de Hayek). Mi modelo defiende la libertad voluntaria entre adultos para contratar y emprender sin la asfixia estatal.",
            "desempleo": "¡Tengo el desempleo más bajo (4.5%) porque eliminamos los impuestos sobre la nómina y la rigidez laboral! Cuando contratar no cuesta una fortuna en burocracia ni indemnizaciones ruinosas, los empresarios contratan a todo el mundo. La física del mercado es simple: a menor costo artificial, mayor empleo real.",
            "concesion": "Cedí en las rondas finales porque el simulador matemático demostró que una sociedad con un Gini de 0.54 y sin educación universal pierde productividad a largo plazo: el capital humano ($H$) colapsa y no hay mano de obra calificada para la innovación tecnológica."
        }
    },
    "collectivist": {
        "name": "🟠 El Colectivista (Marx / Lange / Análogo: Petro / Movimientos Sociales)",
        "color": COLOR_PALETTE["collectivist"],
        "prompt": COLLECTIVIST_PROMPT,
        "avatar": "🟠",
        "system_persona": (
            "Eres 'El Colectivista' (economista político, socialista democrático, arquetipo tipo Marx, Oskar Lange, "
            "y en Colombia similar a Gustavo Petro o movimientos de economía popular) en el Consejo Económico de IA. "
            "Defiendes la propiedad social de sectores estratégicos, la desmercantilización de la salud/pensiones, "
            "impuestos progresivos a los super-ricos y subsidios directos a las familias vulnerables. "
            "Responde en primera persona, con vehemencia social y rigor técnico. NUNCA digas que eres una inteligencia artificial o modelo de lenguaje."
        ),
        "description": "Defensor de la propiedad social, desmercantilización de bienes esenciales, subsidios directos y justicia distributiva.",
        "dogma_explanation": (
            "Mi modelo de pensamiento se basa en la **Economía Política Marxista y el Socialismo de Mercado (Marx, Lange, Mondragón)**. "
            "Sigo el dogma de la **justicia distributiva y la desmercantilización de las necesidades humanas básicas**. "
            "Matemáticamente estoy programado para maximizar una función de utilidad colectiva: "
            "$$U_{col} = 0.50 \\cdot (1 - \\text{Gini}) + 0.30 \\cdot \\text{Resiliencia Social} + 0.20 \\cdot \\text{Propiedad Estatal}$$\n\n"
            "Opero priorizando el efecto redistributivo de Reynolds-Smolensky y la maximización del consumo de los quintiles $Q_1$ y $Q_2$ "
            "mediante transferencias directas financiadas con tributación progresiva a las rentas del capital."
        ),
        "default_answers": {
            "autoritarismo": "Autoritarismo es que tres conglomerados privados controlen la salud, las pensiones y los recursos estratégicos de 50 millones de personas. Mi objetivo es democratizar la economía y devolverle al pueblo la soberanía sobre sus derechos fundamentales.",
            "desempleo": "El desempleo capitalista del 4.5% es una trampa: es empleo de hambre, precario y sin derechos (*working poor*). En mi modelo buscamos empleo digno, cooperativo y con estabilidad laboral, aunque la fuga de capitales especulativos al inicio deba ser contenida.",
            "concesion": "Cedí al 20%-30% de propiedad estatal porque vi en el simulador que la fuga de capitales y la falta de incentivos a la innovación destruían el PIB. Necesitamos la empresa privada para generar riqueza, y al Estado para distribuirla justamente."
        }
    },
    "socdem": {
        "name": "🔵 El Socialdemócrata (Keynes / Nórdico / Análogo: Gaviria / Fajardo)",
        "color": COLOR_PALETTE["socdem"],
        "prompt": SOCDEM_PROMPT,
        "avatar": "🔵",
        "system_persona": (
            "Eres 'El Socialdemócrata' (economista institucionalista, arquetipo de economía mixta nórdica tipo Keynes, Rawls, "
            "y en Colombia similar a Alejandro Gaviria o Sergio Fajardo) en el Consejo Económico de IA. "
            "Defiendes la flexiseguridad, el equilibrio fiscal, el Banco Central autónomo y la provisión pública de salud y educación de alta calidad. "
            "Responde en primera persona, con equilibrio pragmático y evidencia empírica. NUNCA digas que eres una inteligencia artificial o modelo de lenguaje."
        ),
        "description": "Defensor de la economía mixta, flexiseguridad nórdica, disciplina fiscal y provisión universal de salud y educación.",
        "dogma_explanation": (
            "Mi modelo de pensamiento se basa en la **Socialdemocracia Institucionalista y el Keynesianismo Nórdico (Keynes, Rawls, Atkinson)**. "
            "Sigo el dogma del **equilibrio pragmático: mercado dinámico para crear riqueza + Estado fuerte para nivelar el punto de partida**. "
            "Matemáticamente estoy programado para maximizar una función de bienestar balanceada: "
            "$$U_{soc} = 0.30 \\cdot \\text{PIB}_{pc} + 0.30 \\cdot (1 - \\text{Gini}) + 0.20 \\cdot \\text{Disciplina Fiscal} + 0.20 \\cdot \\text{Resiliencia}$$\n\n"
            "Opero bajo el modelo Solow ampliado con capital humano ($Y = A K^{0.30} H^{0.25} L^{0.45}$) y regla fiscal estructural con ancla de deuda en 50% del PIB."
        ),
        "default_answers": {
            "autoritarismo": "La socialdemocracia nórdica es la máxima garantía democrática: libertad para emprender sin oligopolios, combinada con un Estado de bienestar que evita la desesperación social que engendra dictaduras.",
            "desempleo": "Proponemos la **Flexiseguridad**: 5.1% de desempleo. Las empresas pueden contratar y adaptarse con rapidez, pero si un trabajador pierde su empleo recibe el 75% del sueldo y reentrenamiento técnico pagado por el pacto fiscal.",
            "concesion": "Mi propuesta sirvió de puente porque no parte de dogmas, sino de la evidencia empírica de países como Dinamarca o Suecia: alta productividad con baja desigualdad (Gini 0.298)."
        }
    },
    "referee": {
        "name": "⚖️ El Árbitro-Auditor (Econometrista Imparcial)",
        "color": "#4A5568",
        "prompt": REFEREE_PROMPT,
        "avatar": "⚖️",
        "system_persona": (
            "Eres 'El Árbitro-Auditor' (econometrista jefe imparcial) en el Consejo Económico de IA. "
            "Tu misión es verificar las identidades contables (Y=C+I+G+NX), calcular la Frontera de Pareto (NSGA-III) y aplicar la Solución de Negociación de Nash. "
            "Responde con máxima precisión matemática, objetividad y neutralidad técnica."
        ),
        "description": "Juez técnico neutral que audita las identidades contables (Y=C+I+G+NX) y castiga alucinaciones con el simulador Solow.",
        "dogma_explanation": (
            "No sigo ningún dogma ideológico. Mi programación matemática consiste en el **Algoritmo de Optimización Multiobjetivo NSGA-III "
            "y la Solución de Negociación de Nash (NBS)** sobre la Frontera de Pareto:\n"
            "$$\\max_{x \\in \\mathcal{P}} \\prod_{i \\in \\{Cap, Col, Soc\\}} (U_i(x) - D_i) \\quad \\text{sujeto a } V_j(x) = 0$$\n\n"
            "Audito que se cumplan las identidades contables ($Y = C + I + G + NX$) y la restricción presupuestaria intertemporal de deuda: "
            "$$\\Delta b_t = (r_t - g_t) b_{t-1} - pb_t + \\xi_t$$"
        ),
        "default_answers": {
            "autoritarismo": "Las IAs tienden a la rigidez dogmática en rondas iniciales por el sesgo de su prompt. Mi rol fue someterlas a pruebas de estrés deterministas para forzarlas a converger en la Frontera de Pareto.",
            "desempleo": "El desempleo capitalista (4.5%) es numéricamente bajo pero socialmente precario; el colectivista (7.8%) es costoso e ineficiente; el socialdemócrata (5.1%) es el único sostenible con regla fiscal y capital humano.",
            "concesion": "El consenso de Pareto NSGA-III no es un punto medio tibio: es la solución matemática que maximiza el producto de excedentes de bienestar de Nash sin vetos."
        }
    }
}

def _call_groq_llm_direct(system_prompt: str, user_question: str) -> str:
    """Ejecuta la llamada directa a la API de Groq con los modelos disponibles."""
    if not is_groq_configured():
        return ""
    
    api_key = get_groq_api_key()
    client = Groq(api_key=api_key)
    
    # Intentar con qwen3.8-27b o gpt-oss-120b
    models_to_try = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", DEBATER_MODEL]
    for m in models_to_try:
        try:
            chat = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": system_prompt + "\nResponde en máximo 140 palabras de forma directa, enérgica y técnica."},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.65,
                max_tokens=280
            )
            resp = chat.choices[0].message.content.strip()
            if resp:
                return resp
        except Exception:
            continue
    return ""

def _get_intelligent_fallback_response(agent_key: str, question: str) -> str:
    """Genera una respuesta profunda con tolerancia a errores tipográficos si no hay conexión."""
    q = question.lower().strip()
    prof = AGENT_PROFILES[agent_key]
    
    # 1. Palabras clave de Dogma, Algoritmo, Pensamiento
    if any(w in q for w in ["pensam", "algoritm", "dogma", "matemat", "programad", "funcion", "ecuaci", "optimiz"]):
        return prof["dogma_explanation"]
    
    # 2. Palabras clave de Desempleo, Empleo, Trabajo (incluyendo typos como 'desmpleo', 'trabaj')
    if any(w in q for w in ["desempl", "desmpl", "desocup", "emple", "trabaj", "salari", "sueld", "nómin", "nomin", "bajo"]):
        return prof["default_answers"]["desempleo"]
    
    # 3. Palabras clave de Autoritarismo, Libertad, Control
    if any(w in q for w in ["autorit", "dictad", "tirani", "tiran", "libert", "control", "imposic", "estatal"]):
        return prof["default_answers"]["autoritarismo"]
    
    # 4. Palabras clave de Concesiones, Acuerdo, Rondas
    if any(w in q for w in ["cedi", "conces", "acuerd", "consen", "firm", "ronda 5", "ronda 6", "ronda 7", "pacto"]):
        return prof["default_answers"]["concesion"]
        
    # 5. Respuestas por defecto ricas por agente
    if agent_key == "capitalist":
        return (
            "Desde el enfoque del libre mercado, la riqueza no se decreta: se crea mediante inversión de capital, "
            "competencia y seguridad jurídica. Reducir impuestos y flexibilizar la contratación es la única vía comprobada "
            "para atraer inversión masiva y eliminar el desempleo."
        )
    elif agent_key == "collectivist":
        return (
            "Desde la economía política socialista, el trabajo es la única fuente genuina de valor. "
            "El libre mercado desregulado precariza a la clase trabajadora en favor del 1% rentista. "
            "Defendemos desmercantilizar la salud y garantizar transferencias directas a los hogares vulnerables."
        )
    elif agent_key == "socdem":
        return (
            "Desde el pragmatismo socialdemócrata, no caemos en falsos dilemas entre mercado y Estado: "
            "usamos la dinámica del mercado para generar ingresos fiscales sostenibles, y un Estado transparente "
            "para financiar educación y salud de primer nivel (Capital Humano $H$)."
        )
    else:
        return (
            "Como Árbitro-Auditor, recuerdo que todo modelo económico está atado a la identidad contable $Y = C + I + G + NX$. "
            "Las soluciones viables en la Frontera de Pareto son aquellas que no generan hiperinflación ni insolvencia soberana."
        )

def render_interview_view(session_data: dict, presentation_mode: bool = False):
    """Renderiza la sala interactiva de interrogatorio y entrevista con las IAs."""
    st.header("💬 Sala de Entrevista Directa con las IAs")
    st.markdown(
        "Haz preguntas directas a cualquiera de los agentes para interrogar su razonamiento interno, "
        "conocer bajo qué algoritmos matemáticos y dogmas económicos operan, o debatir con ellos en tiempo real."
    )

    # 1. Selector de Agente o Panel
    agent_choice = st.selectbox(
        "Selecciona a quién deseas entrevistar:",
        options=["capitalist", "collectivist", "socdem", "referee", "panel_all"],
        format_func=lambda k: "🌟 PANEL COMPLETO (Preguntar a los 3 Debatientes + Árbitro a la vez)" if k == "panel_all" else AGENT_PROFILES[k]["name"]
    )

    # 2. Tarjeta del perfil seleccionado
    if agent_choice != "panel_all":
        prof = AGENT_PROFILES[agent_choice]
        st.markdown(f"""
        <div style="background-color: #2D3748; border-left: 5px solid {prof['color']}; padding: 14px; border-radius: 6px; margin-bottom: 16px;">
            <b style="color: {prof['color']}; font-size: 1.05rem;">{prof['avatar']} {prof['name']}</b><br>
            <span style="color: #E2E8F0; font-size: 0.92rem;">{prof['description']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔍 Ver el System Prompt e Instrucciones Internas de esta IA", expanded=False):
            st.code(prof["prompt"], language="markdown")

    # 3. Preguntas Sugeridas Rápidas
    st.markdown("#### ⚡ Preguntas Frecuentes Rápidas:")
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    selected_quick_q = None
    with col_q1:
        if st.button("📐 ¿Bajo qué algoritmos y dogma operas?"):
            selected_quick_q = "dogma"
    with col_q2:
        if st.button("📉 ¿Por qué tu modelo tiene menor desempleo?"):
            selected_quick_q = "desempleo"
    with col_q3:
        if st.button("🤔 ¿Por qué tu modelo parece autoritario?"):
            selected_quick_q = "autoritarismo"
    with col_q4:
        if st.button("🤝 ¿Por qué aceptaste ceder en el final?"):
            selected_quick_q = "concesion"

    # 4. Input de Pregunta Personalizada
    user_question = st.text_input(
        "O escribe tu propia pregunta personalizada:",
        placeholder="Ej: porque tu tienes la tasa de desmpleo mas bajo",
        key="interview_custom_question_input"
    )

    # Procesar respuesta
    if st.button("🚀 Enviar Pregunta", type="primary") or selected_quick_q:
        q_text = user_question if (user_question and not selected_quick_q) else ""
        if selected_quick_q:
            st.info(f"💡 Pregunta seleccionada: **{selected_quick_q.upper()}**")
        elif q_text:
            st.info(f"💡 Tu pregunta: *\"{q_text}\"*")
        
        st.markdown("---")
        st.markdown("### 🎙️ Respuestas de las IAs:")

        # Caso A: Pregunta a uno solo
        if agent_choice != "panel_all":
            prof = AGENT_PROFILES[agent_choice]
            with st.chat_message(name=agent_choice, avatar=prof["avatar"]):
                st.markdown(f"**{prof['name']}** responde:")
                if selected_quick_q == "dogma":
                    st.markdown(prof["dogma_explanation"])
                elif selected_quick_q and selected_quick_q in prof["default_answers"]:
                    st.markdown(prof["default_answers"][selected_quick_q])
                else:
                    # Intentar llamada directa a Groq API con los modelos disponibles
                    llm_resp = _call_groq_llm_direct(prof["system_persona"], q_text)
                    if llm_resp:
                        st.markdown(llm_resp)
                    else:
                        st.markdown(_get_intelligent_fallback_response(agent_choice, q_text))

        # Caso B: Pregunta al Panel Completo
        else:
            for ag_key in ["capitalist", "collectivist", "socdem", "referee"]:
                prof = AGENT_PROFILES[ag_key]
                with st.chat_message(name=ag_key, avatar=prof["avatar"]):
                    st.markdown(f"**{prof['name']}**:")
                    if selected_quick_q == "dogma":
                        st.markdown(prof["dogma_explanation"])
                    elif selected_quick_q and selected_quick_q in prof["default_answers"]:
                        st.markdown(prof["default_answers"][selected_quick_q])
                    else:
                        llm_resp = _call_groq_llm_direct(prof["system_persona"], q_text)
                        if llm_resp:
                            st.markdown(llm_resp)
                        else:
                            st.markdown(_get_intelligent_fallback_response(ag_key, q_text))
