"""
Módulo de Gráficos Intuitivos y Explicaciones Universales para Modo Fácil.
Implementa:
1. Regla de Posiciones ('Policymeter') horizontal con etiquetado directo.
2. Termómetro / Medidor circular de convergencia (0-100%).
3. Barras horizontales comparativas con etiquetas sobre las barras.
4. Componente estándar render_explained_chart() con las 4 partes obligatorias:
   - Qué muestra
   - Cómo leerlo
   - Qué significa aquí
   - Ojo con esto
   + 'Modo Explicado' interactivo.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import math
from typing import Dict, Any, List, Optional

from src.app.viz.metrics_catalog import COLOR_PALETTE, SYSTEM_LABELS
from src.app.viz.round_summary_generator import POLICY_POPULAR_NAMES, POPULAR_METRICS_CONFIG, get_metric_status_tag

def render_explained_box(
    what_shows: str,
    how_to_read: str,
    what_means_here: str,
    watch_out: str,
    key_prefix: str = "chart",
):
    """Renderiza el bloque estándar de 4 partes junto a cualquier gráfico en Modo Fácil."""
    st.markdown(f"""
    <div style="background-color: #1A202C; border: 1px solid #4A5568; border-radius: 8px; padding: 14px 18px; margin-top: 10px; margin-bottom: 16px;">
        <div style="margin-bottom: 8px;">
            <b style="color: #63B3ED;">📌 Qué muestra:</b> <span style="color: #EDF2F7; font-size: 0.92rem;">{what_shows}</span>
        </div>
        <div style="margin-bottom: 8px;">
            <b style="color: #F6E05E;">👀 Cómo leerlo:</b> <span style="color: #E2E8F0; font-size: 0.92rem;">{how_to_read}</span>
        </div>
        <div style="margin-bottom: 8px;">
            <b style="color: #68D391;">💡 Qué significa aquí:</b> <span style="color: #EDF2F7; font-size: 0.92rem;">{what_means_here}</span>
        </div>
        <div>
            <b style="color: #FC8181;">⚠️ Ojo con esto:</b> <span style="color: #FEB2B2; font-size: 0.92rem;">{watch_out}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_policymeter_chart(
    vectors: Dict[str, Any],
    consensus_vector: Optional[Any] = None,
    highlight_params: Optional[List[str]] = None,
    show_explained_mode: bool = False,
) -> go.Figure:
    """
    Regla de Posiciones ('Policymeter'): Una línea horizontal por cada política clave
    con los puntos de cada agente (🔴 Capitalista, 🟠 Colectivista, 🔵 Socialdemócrata)
    y el punto dorado (🟡 Consenso).
    """
    params = highlight_params or [
        "max_tax_rate",
        "public_spending_gdp",
        "state_ownership",
        "labor_protection",
        "trade_openness",
    ]
    
    # Normalizar vectores de entrada a diccionarios
    clean_vectors = {}
    if isinstance(vectors, dict):
        for k, v in vectors.items():
            if hasattr(v, "to_dict"):
                clean_vectors[k] = v.to_dict()
            elif hasattr(v, "model_dump"):
                clean_vectors[k] = v.model_dump()
            elif isinstance(v, dict):
                clean_vectors[k] = v
            else:
                clean_vectors[k] = {}

    clean_consensus = {}
    if consensus_vector is not None:
        if hasattr(consensus_vector, "to_dict"):
            clean_consensus = consensus_vector.to_dict()
        elif hasattr(consensus_vector, "model_dump"):
            clean_consensus = consensus_vector.model_dump()
        elif isinstance(consensus_vector, dict):
            clean_consensus = consensus_vector

    fig = go.Figure()
    
    for idx, param in enumerate(params):
        param_label = POLICY_POPULAR_NAMES.get(param, param)
        y_val = len(params) - 1 - idx
        
        # Línea de fondo del rango 0 a 100%
        fig.add_trace(go.Scatter(
            x=[0, 1.0],
            y=[y_val, y_val],
            mode="lines",
            line=dict(color="#4A5568", width=4),
            hoverinfo="skip",
            showlegend=False,
        ))
        
        # Puntos de los agentes
        for ag_id in ["capitalist", "collectivist", "socdem"]:
            if ag_id in clean_vectors and param in clean_vectors[ag_id]:
                val = clean_vectors[ag_id][param]
                fig.add_trace(go.Scatter(
                    x=[val],
                    y=[y_val],
                    mode="markers+text" if show_explained_mode else "markers",
                    marker=dict(
                        color=COLOR_PALETTE.get(ag_id, "#ECC94B"),
                        size=14,
                        line=dict(color="#FFFFFF", width=1.5)
                    ),
                    name=SYSTEM_LABELS.get(ag_id, ag_id),
                    text=[f"{val:.0%}"] if show_explained_mode else None,
                    textposition="top center",
                    textfont=dict(color="#FFFFFF", size=10),
                    hovertemplate=f"<b>{SYSTEM_LABELS.get(ag_id, ag_id)}</b><br>{param_label}: %{{x:.1%}}<extra></extra>",
                    showlegend=(idx == 0),
                ))
                
        # Punto de Consenso (si existe)
        if clean_consensus and param in clean_consensus:
            c_val = clean_consensus[param]
            fig.add_trace(go.Scatter(
                x=[c_val],
                y=[y_val],
                mode="markers+text" if show_explained_mode else "markers",
                marker=dict(
                    color="#ECC94B",
                    size=18,
                    symbol="star",
                    line=dict(color="#FFFFFF", width=2)
                ),
                name="🟡 Consenso Final",
                text=[f"⭐ {c_val:.0%}"] if show_explained_mode else None,
                textposition="bottom center",
                textfont=dict(color="#ECC94B", size=11, family="Arial Black"),
                hovertemplate=f"<b>⭐ Consenso Final</b><br>{param_label}: %{{x:.1%}}<extra></extra>",
                showlegend=(idx == 0),
            ))

    fig.update_layout(
        title="📏 Regla de Posiciones (Policymeter): ¿Dónde se ubica cada sistema?",
        xaxis=dict(
            title="Intensidad de la Política (0% = Mínimo | 100% = Máximo)",
            range=[-0.05, 1.05],
            tickformat=".0%",
            color="#A0AEC0",
            gridcolor="#2D3748"
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(params))),
            ticktext=[POLICY_POPULAR_NAMES.get(p, p) for p in reversed(params)],
            color="#FFFFFF",
            gridcolor="#2D3748"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26, 32, 44, 0.6)",
        height=340,
        margin=dict(l=150, r=40, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#E2E8F0")
        )
    )
    
    return fig

def render_convergence_gauge(convergence_pct: float) -> go.Figure:
    """Medidor tipo termómetro / velocímetro de convergencia (0-100%)."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=convergence_pct,
        number={'suffix': "%", 'font': {'size': 32, 'color': "#ECC94B"}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "#A0AEC0", 'tickwidth': 2},
            'bar': {'color': "#3182CE", 'thickness': 0.3},
            'bgcolor': "#1A202C",
            'borderwidth': 2,
            'bordercolor': "#4A5568",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(245, 101, 101, 0.3)'},
                {'range': [40, 75], 'color': 'rgba(236, 201, 75, 0.3)'},
                {'range': [75, 100], 'color': 'rgba(72, 187, 120, 0.35)'},
            ],
            'threshold': {
                'line': {'color': "#48BB78", 'width': 4},
                'thickness': 0.75,
                'value': 85.0
            }
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#EDF2F7")
    )
    return fig

def render_popular_metrics_cards(
    metrics_by_system: Dict[str, Dict[str, float]],
    show_diff_against: Optional[str] = None,
):
    """
    Renderiza las 6 métricas populares con tarjetas visuales,
    semáforos cualitativos ('🟢 Crecimiento Alto', '🟢 Muy Parejo', etc.)
    y formato amigable.
    """
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3, col1, col2, col3]
    
    consensus_metrics = metrics_by_system.get("consensus", {})
    
    for idx, (m_key, cfg) in enumerate(POPULAR_METRICS_CONFIG.items()):
        val = float(consensus_metrics.get(m_key, 0.0))
        if m_key in ["unemployment_avg", "max_debt_gdp", "terminal_debt_gdp"] and 0 < val <= 1.0:
            val = val * 100.0
        formatted_val = cfg["format"].format(val)
        tag_label, tag_color = get_metric_status_tag(m_key, val)
        
        target_col = cols[idx]
        with target_col:
            st.markdown(f"""
            <div style="background-color: #2D3748; border: 1px solid #4A5568; border-radius: 8px; padding: 14px 16px; margin-bottom: 14px;">
                <div style="font-size: 0.82rem; color: #A0AEC0; text-transform: uppercase; font-weight: 700;">{cfg['title']}</div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 4px; margin-bottom: 6px;">
                    <span style="font-size: 1.6rem; font-weight: 800; color: #FFFFFF;">{formatted_val}</span>
                    <span style="font-size: 0.8rem; background-color: rgba(26, 32, 44, 0.8); color: {tag_color}; padding: 2px 8px; border-radius: 4px; border: 1px solid {tag_color};">{tag_label}</span>
                </div>
                <div style="font-size: 0.83rem; color: #CBD5E0; line-height: 1.4;">{cfg['description']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_horizontal_comparison_bars(
    df_metrics: pd.DataFrame,
    metric_key: str = "terminal_gdp_pc",
    title: str = "Comparación de Crecimiento Económico",
) -> go.Figure:
    """Barras horizontales comparativas simples con etiquetas directas sobre las barras."""
    cfg = POPULAR_METRICS_CONFIG.get(metric_key, {"format": "{:.2f}", "title": metric_key})
    
    labels = []
    values = []
    colors = []
    
    # Caso 1: df_metrics viene de compute_all_metrics_table (filas = métricas, columnas = sistemas)
    if "metric_key" in df_metrics.columns:
        match_rows = df_metrics[df_metrics["metric_key"] == metric_key]
        if not match_rows.empty:
            m_row = match_rows.iloc[0].to_dict()
            systems_order = [
                ("capitalist", "🔴 Capitalista", COLOR_PALETTE["capitalist"]),
                ("collectivist", "🟠 Colectivista", COLOR_PALETTE["collectivist"]),
                ("socdem", "🔵 Socialdemócrata", COLOR_PALETTE["socdem"]),
                ("consensus", "🟡 Consenso Final", "#ECC94B"),
            ]
            for s_id, s_name, s_col in systems_order:
                if s_id in m_row:
                    labels.append(s_name)
                    values.append(float(m_row[s_id]))
                    colors.append(s_col)
    else:
        # Caso 2: df_metrics tiene filas = sistemas
        for item in df_metrics.to_dict(orient="records"):
            sys_name = item.get("system_name", item.get("Sistema", item.get("pos_id", "Sistema")))
            val = float(item.get(metric_key, 0.0))
            labels.append(sys_name)
            values.append(val)
            
            s_low = str(sys_name).lower()
            if "capitalista" in s_low or "capitalist" in s_low:
                colors.append(COLOR_PALETTE["capitalist"])
            elif "colectivista" in s_low or "collectivist" in s_low:
                colors.append(COLOR_PALETTE["collectivist"])
            elif "socialdem" in s_low or "socdem" in s_low:
                colors.append(COLOR_PALETTE["socdem"])
            else:
                colors.append("#ECC94B")

    formatted_texts = [cfg["format"].format(v) if isinstance(v, (int, float)) and not np.isnan(v) else "N/A" for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker=dict(color=colors, line=dict(color="#FFFFFF", width=1)),
        text=formatted_texts,
        textposition="inside",
        textfont=dict(color="#FFFFFF", size=12, family="Arial Black"),
        hovertemplate="<b>%{y}</b><br>Resultado: %{text}<extra></extra>",
    ))

    fig.update_layout(
        title=f"📊 {title}",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26, 32, 44, 0.6)",
        xaxis=dict(color="#A0AEC0", gridcolor="#2D3748"),
        yaxis=dict(color="#FFFFFF", gridcolor="#2D3748"),
        height=260,
        margin=dict(l=160, r=30, t=40, b=40),
    )
    
    return fig
