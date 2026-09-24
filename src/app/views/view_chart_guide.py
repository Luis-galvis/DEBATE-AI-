"""
Vista Pedagógica: ¿Cómo leer los gráficos de este proyecto?
Explica de manera intuitiva y con ejemplos comentados cada tipo de gráfico utilizado:
1. Regla de Posiciones ('Policymeter')
2. Termómetro / Medidor de Convergencia
3. Barras Horizontales Comparativas
4. Gráfico de Radar Multidimensional
5. Frontera de Pareto 2D
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

def render_chart_guide_view(presentation_mode: bool = False):
    """Renderiza la guía visual interactiva de lectura de gráficos."""
    st.header("📊 ¿Cómo leer los gráficos de este proyecto?")
    st.markdown("Una guía rápida con ejemplos prácticos para interpretar cualquier visualización del Consejo Económico de IA en segundos.")

    g_tabs = st.tabs([
        "📏 1. Regla de Posiciones (Policymeter)",
        "🌡️ 2. Termómetro de Convergencia",
        "📊 3. Barras Horizontales",
        "🕸️ 4. Radar Multidimensional (Avanzado)",
        "📈 5. Frontera de Pareto (Avanzado)",
    ])

    # 1. Regla de Posiciones
    with g_tabs[0]:
        st.subheader("📏 Regla de Posiciones ('Policymeter')")
        st.markdown("""
        * **Qué es:** Una línea horizontal para cada política económica clave, donde cada punto representa la propuesta de un agente (de 0% a 100%).
        * **Cómo leerlo:** 
          * El extremo izquierdo (0%) indica intervención mínima o impuestos bajos.
          * El extremo derecho (100%) indica máxima intervención estatal o impuestos altos.
          * La **estrella dorada (⭐)** marca el punto de acuerdo alcanzado.
        """)
        
        # Mini ejemplo didáctico
        fig_demo1 = go.Figure()
        fig_demo1.add_trace(go.Scatter(x=[0, 1.0], y=[0, 0], mode="lines", line=dict(color="#4A5568", width=5), showlegend=False))
        fig_demo1.add_trace(go.Scatter(x=[0.15], y=[0], mode="markers+text", marker=dict(color="#F56565", size=14), name="🔴 Capitalista (15%)", text=["🔴 15%"], textposition="top center"))
        fig_demo1.add_trace(go.Scatter(x=[0.80], y=[0], mode="markers+text", marker=dict(color="#ED8936", size=14), name="🟠 Colectivista (80%)", text=["🟠 80%"], textposition="top center"))
        fig_demo1.add_trace(go.Scatter(x=[0.38], y=[0], mode="markers+text", marker=dict(color="#ECC94B", size=18, symbol="star"), name="⭐ Consenso (38%)", text=["⭐ 38%"], textposition="bottom center"))
        fig_demo1.update_layout(
            title="Ejemplo: Impuesto Máximo Propuesto",
            xaxis=dict(range=[-0.05, 1.05], tickformat=".0%", color="#A0AEC0"),
            yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(26, 32, 44, 0.6)",
            height=200,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_demo1, use_container_width=True, key="chart_guide_demo1_chart")

    # 2. Termómetro de Convergencia
    with g_tabs[1]:
        st.subheader("🌡️ Termómetro / Medidor de Convergencia")
        st.markdown("""
        * **Qué es:** Un porcentaje de 0% a 100% que mide qué tan cerca están los 3 agentes de ponerse de acuerdo.
        * **Cómo leerlo:**
          * **0% a 40% (Rojo):** Máxima polarización; cada agente defiende su postura inicial sin ceder.
          * **40% a 75% (Amarillo):** Negociación activa; empiezan a reconocer debilidades y hacer concesiones.
          * **75% a 100% (Verde):** Alta convergencia; las diferencias se reducen a ajustes menores.
        """)

    # 3. Barras Horizontales
    with g_tabs[2]:
        st.subheader("📊 Barras Horizontales con Etiquetado Directo")
        st.markdown("""
        * **Qué es:** Comparación directa de una métrica económica concreta entre los 4 modelos.
        * **Cómo leerlo:**
          * Las barras más largas indican un valor mayor de la métrica (ej. más PIB o más gasto).
          * El número está escrito directamente dentro de la barra para no tener que buscarlo en tablas complejas.
        """)

    # 4. Radar Multidimensional
    with g_tabs[3]:
        st.subheader("🕸️ Radar Multidimensional (Vista Técnica)")
        st.markdown("""
        * **Qué es:** Un polígono que compara varias dimensiones simultáneamente en una sola figura.
        * **Cómo leerlo:**
          * El centro representa valor 0 y el borde exterior representa valor máximo.
          * Un área más amplia significa mayor presencia de esa política o mayor intensidad en los parámetros.
        """)

    # 5. Frontera de Pareto
    with g_tabs[4]:
        st.subheader("📈 Frontera de Pareto y Trade-Offs (Vista Técnica)")
        st.markdown("""
        * **Qué es:** La curva matemática de soluciones donde no es posible mejorar un objetivo (ej. crecimiento) sin empeorar otro (ej. igualdad).
        * **Cómo leerlo:**
          * Los puntos sobre la curva representan combinaciones óptimas eficientes.
          * Los puntos fuera de la curva hacia abajo son ineficientes o matemáticamente insostenibles.
        """)
