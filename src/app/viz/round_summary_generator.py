"""
Módulo Generador de Tarjetas de Cierre por Ronda (Rondas 1 a 7).
Genera de forma determinista y estructurada los 5 bloques para cada ronda:
1. Qué pasó en esta ronda.
2. La postura de cada uno en palabras simples (Capitalista, Colectivista, Socialdemócrata).
3. ¿Se están poniendo de acuerdo? (Medidor 0-100% de convergencia + coinciden vs chocan).
4. Consenso hasta ahora (Punto medio provisional en R1-R6 vs Modelo Oficial en R7).
5. Lo que cambió desde la ronda anterior.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

from src.simulation.policy_vector import (
    POLICY_DIMENSIONS,
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)
from src.app.viz.metrics_catalog import COLOR_PALETTE, SYSTEM_LABELS

# Nombres populares para las 10 dimensiones de política
POLICY_POPULAR_NAMES = {
    "state_ownership": "Propiedad del Estado",
    "max_tax_rate": "Impuesto Máximo",
    "tax_progressivity": "Progresividad de Impuestos",
    "public_spending_gdp": "Gasto Social y Servicios",
    "social_transfers_coverage": "Cobertura de Ayudas y Subsidios",
    "market_regulation": "Regulación de Empresas",
    "labor_protection": "Protección a los Trabajadores",
    "trade_openness": "Apertura al Comercio Exterior",
    "fiscal_rule_strictness": "Disciplina Fiscal (Cero Deuda)",
    "central_bank_independence": "Independencia del Banco Central",
}

# Las 6 Métricas Populares Titulares con Semáforos Cualitativos
POPULAR_METRICS_CONFIG = {
    "terminal_gdp_pc": {
        "title": "Crecimiento Económico",
        "description": "Ingreso promedio por habitante proyectado a 30 años.",
        "format": "${:,.0f} USD",
        "better": "high",
        "levels": [(14000, "🟢 Crecimiento Alto"), (9000, "🟡 Crecimiento Moderado"), (0, "🔴 Crecimiento Bajo")]
    },
    "gini_avg": {
        "title": "Igualdad de Ingresos",
        "description": "Distribución del ingreso (más bajo = más parejo).",
        "format": "{:.3f}",
        "better": "low",
        "levels": [(0.42, "🟢 Muy Parejo"), (0.50, "🟡 Moderado"), (1.0, "🔴 Muy Desigual")]
    },
    "unemployment_avg": {
        "title": "Tasa de Desempleo",
        "description": "Porcentaje promedio de fuerza laboral sin empleo.",
        "format": "{:.1f}%",
        "better": "low",
        "levels": [(6.0, "🟢 Empleo Fuerte"), (10.0, "🟡 Desempleo Moderado"), (100.0, "🔴 Desempleo Alto")]
    },
    "max_debt_gdp": {
        "title": "Deuda Pública Máxima",
        "description": "Nivel máximo de deuda del Estado respecto al PIB.",
        "format": "{:.1f}%",
        "better": "low",
        "levels": [(50.0, "🟢 Deuda Sostenible"), (80.0, "🟡 Alerta Fiscal"), (500.0, "🔴 Riesgo de Quiebra")]
    },
    "social_welfare_index": {
        "title": "Bienestar y Servicios",
        "description": "Índice que combina salud, educación y cobertura social.",
        "format": "{:.1f} / 100",
        "better": "high",
        "levels": [(65, "🟢 Bienestar Alto"), (50, "🟡 Bienestar Medio"), (0, "🔴 Bienestar Frágil")]
    },
    "resilience_score": {
        "title": "Resistencia a Crisis",
        "description": "Capacidad de recuperarse ante pandemias y choques.",
        "format": "{:.1f} / 100",
        "better": "high",
        "levels": [(70, "🟢 Muy Resistente"), (50, "🟡 Resistencia Media"), (0, "🔴 Vulnerable")]
    }
}

def get_metric_status_tag(metric_key: str, value: float) -> Tuple[str, str]:
    """Devuelve la etiqueta de semáforo cualitativo y color para una métrica popular."""
    cfg = POPULAR_METRICS_CONFIG.get(metric_key)
    if not cfg:
        return "ℹ️ Informativo", "#A0AEC0"
    
    val = float(value)
    if metric_key in ["unemployment_avg", "max_debt_gdp", "terminal_debt_gdp"] and 0 < val <= 1.0:
        val = val * 100.0
    
    if cfg["better"] == "high":
        for threshold, label in cfg["levels"]:
            if val >= threshold:
                color = "#48BB78" if "🟢" in label else ("#ECC94B" if "🟡" in label else "#F56565")
                return label, color
    else:
        for threshold, label in cfg["levels"]:
            if val <= threshold:
                color = "#48BB78" if "🟢" in label else ("#ECC94B" if "🟡" in label else "#F56565")
                return label, color
                
    return "🟡 En Rango", "#ECC94B"

def calculate_round_convergence_score(
    cap_vec: Dict[str, float],
    col_vec: Dict[str, float],
    soc_vec: Dict[str, float]
) -> Tuple[float, List[Tuple[str, float]], List[Tuple[str, float]]]:
    """
    Calcula el porcentaje de convergencia (0 a 100%) entre los 3 agentes
    y determina en qué políticas coinciden más y en cuáles siguen chocando.
    """
    param_distances = []
    
    for param in POLICY_DIMENSIONS:
        v_cap = cap_vec.get(param, 0.5)
        v_col = col_vec.get(param, 0.5)
        v_soc = soc_vec.get(param, 0.5)
        
        # Dispersión (rango entre el valor máximo y mínimo propuesto)
        spread = max(v_cap, v_col, v_soc) - min(v_cap, v_col, v_soc)
        param_distances.append((param, spread))
        
    # Ordenar por dispersión (menor = mayor coincidencia)
    sorted_by_spread = sorted(param_distances, key=lambda x: x[1])
    
    # 2 parámetros con mayor coincidencia
    coinciden = [(POLICY_POPULAR_NAMES.get(p, p), s) for p, s in sorted_by_spread[:2]]
    # 2 parámetros con mayor choque
    chocan = [(POLICY_POPULAR_NAMES.get(p, p), s) for p, s in sorted_by_spread[-2:]]
    
    # Puntuación global de convergencia: 100% cuando el spread promedio es 0, 0% cuando es 1
    avg_spread = np.mean([s for _, s in param_distances])
    convergence_pct = max(0.0, min(100.0, (1.0 - avg_spread) * 100.0))
    
    return float(convergence_pct), coinciden, chocan

def compute_provisional_midpoint_vector(
    cap_vec: Dict[str, float],
    col_vec: Dict[str, float],
    soc_vec: Dict[str, float]
) -> Dict[str, float]:
    """Calcula el vector de punto medio aritmético provisional para las rondas 1 a 6."""
    midpoint = {}
    for param in POLICY_DIMENSIONS:
        v_cap = cap_vec.get(param, 0.5)
        v_col = col_vec.get(param, 0.5)
        v_soc = soc_vec.get(param, 0.5)
        midpoint[param] = round(float(np.mean([v_cap, v_col, v_soc])), 3)
    return midpoint

def generate_round_summary_card(
    session_data: Dict[str, Any],
    round_num: int
) -> Dict[str, Any]:
    """
    Genera la tarjeta de cierre completa para una ronda específica (1 a 7).
    """
    from src.app.viz.debate_adapter import _normalize_session_data
    norm_data = _normalize_session_data(session_data)
    rounds = norm_data.get("rounds", [])
    if not rounds or round_num < 1 or round_num > len(rounds):
        return {
            "round_number": round_num,
            "what_happened": "No hay datos de esta ronda.",
            "stances": {},
            "convergence_pct": 0.0,
            "coinciden": [],
            "chocan": [],
            "consensus_status_label": "🟡 Sin datos",
            "consensus_points": [],
            "what_changed": "Inicio de la simulación.",
            "is_final_official": False
        }
        
    current_round = rounds[round_num - 1]
    prev_round = rounds[round_num - 2] if round_num > 1 else None
    
    # Extraer vectores vigentes de la ronda
    current_vectors = {
        "capitalist": CAPITALIST_INITIAL_VECTOR.to_dict(),
        "collectivist": COLLECTIVIST_INITIAL_VECTOR.to_dict(),
        "socdem": SOCDEM_INITIAL_VECTOR.to_dict(),
    }
    
    for sp in current_round.get("speeches", []):
        ag = sp.get("agent")
        if ag in current_vectors and sp.get("current_vector"):
            current_vectors[ag] = sp["current_vector"]
            
    # Extraer vectores previos para comparar cambios
    prev_vectors = {
        "capitalist": CAPITALIST_INITIAL_VECTOR.to_dict(),
        "collectivist": COLLECTIVIST_INITIAL_VECTOR.to_dict(),
        "socdem": SOCDEM_INITIAL_VECTOR.to_dict(),
    }
    if prev_round:
        for sp in prev_round.get("speeches", []):
            ag = sp.get("agent")
            if ag in prev_vectors and sp.get("current_vector"):
                prev_vectors[ag] = sp["current_vector"]

    # 1. Qué pasó en esta ronda (Lenguaje cotidiano y frases cortas)
    narrative_templates = {
        1: "Cada agente presentó su plan de inicio. El liberal pidió libre mercado. El colectivista pidió empresas públicas. El socialdemócrata propuso un punto medio.",
        2: "El simulador proyectó 30 años de datos. El plan liberal crea más riqueza pero abre brechas. El plan social cuida a todos pero frena la inversión.",
        3: "Los agentes se hicieron preguntas duras con datos reales. El árbitro auditó las cuentas y exigió admitir riesgos de deuda y de empleo.",
        4: "Se probaron los planes ante crisis y choques de salud. El modelo mixto resistió mejor gracias a sus ayudas sociales directas.",
        5: "Llegó el momento de ceder: el grupo social aceptó cuidar la inversión privada. El grupo liberal aceptó fijar un piso social de ayuda.",
        6: "Los agentes ajustaron sus números finales en la mesa. Las distancias se acortaron mucho en impuestos y en metas de ahorro.",
        7: "El motor de datos halló el balance óptimo para el país. El Árbitro bautizó el gran acuerdo y los tres votaron a favor."
    }
    what_happened = narrative_templates.get(round_num, f"Debate estructurado y contrastación de evidencia en la Ronda {round_num}.")

    # 2. Posturas en palabras simples (Defiende, Cedió, No negocia)
    stances_templates = {
        1: {
            "capitalist": {"defiende": "Libre mercado, impuestos del 15% y regla fiscal estricta.", "cedio": "Aún en postura inicial pura.", "no_negocia": "Derechos de propiedad privada y Banco Central independiente."},
            "collectivist": {"defiende": "85% de propiedad pública y gasto social del 85% del PIB.", "cedio": "Aún en postura inicial pura.", "no_negocia": "Servicios esenciales desmercantilizados."},
            "socdem": {"defiende": "Economía mixta nórdica con impuestos progresivos del 45%.", "cedio": "Aún en postura inicial pura.", "no_negocia": "Red de seguridad social universal."}
        },
        2: {
            "capitalist": {"defiende": "El crecimiento como motor para erradicar la pobreza.", "cedio": "Reconoció que la desigualdad inicial sube a Gini 0.54.", "no_negocia": "Libre comercio y baja regulación."},
            "collectivist": {"defiende": "La igualdad distributiva (Gini 0.38) como meta suprema.", "cedio": "Admitió que el PIB per cápita se frena por menor capital.", "no_negocia": "Transferencias universales."},
            "socdem": {"defiende": "El balance entre incentivos y cohesión social.", "cedio": "Aceptó que el gasto alto eleva la deuda al 62%.", "no_negocia": "Educación y salud públicas de calidad."}
        },
        3: {
            "capitalist": {"defiende": "Aceleración de la productividad (TFP).", "cedio": "Admitió que la falta de cobertura social genera crisis de demanda.", "no_negocia": "Estabilidad monetaria."},
            "collectivist": {"defiende": "Democracia en los lugares de trabajo.", "cedio": "Aceptó que la planificación excesiva desincentiva la innovación.", "no_negocia": "Protección laboral estricta."},
            "socdem": {"defiende": "Inversión pública focalizada en capital humano.", "cedio": "Reconoció que los impuestos corporativos excesivos ahuyentan la I+D.", "no_negocia": "Progresividad fiscal."}
        },
        4: {
            "capitalist": {"defiende": "Flexibilidad laboral para absorber choques externos.", "cedio": "Aceptó que ante pandemias el Estado debe actuar como prestamista.", "no_negocia": "Apertura comercial."},
            "collectivist": {"defiende": "Seguro de salud estatal frente a emergencias.", "cedio": "Admitió que sin reservas fiscales el país cae en insolvencia.", "no_negocia": "Acceso universal a vacunas y medicinas."},
            "socdem": {"defiende": "Estabilizadores automáticos que amortiguan la caída del PIB.", "cedio": "Aceptó fijar un tope a la deuda pública en tiempos de calma.", "no_negocia": "Seguro de desempleo."}
        },
        5: {
            "capitalist": {"defiende": "Tasa impositiva máxima del 28% y estímulos a la inversión.", "cedio": "Aceptó financiar transferencias sociales con un piso del 30%.", "no_negocia": "Libre fijación de precios en el mercado."},
            "collectivist": {"defiende": "Salarios dignos y servicios públicos robustos.", "cedio": "Redujo la propiedad estatal propuesta del 85% al 40%.", "no_negocia": "Progresividad tributaria mínima del 50%."},
            "socdem": {"defiende": "Pacto social tripartite (empresas, trabajadores y Estado).", "cedio": "Flexibilizó regulaciones burocráticas menores.", "no_negocia": "Regla fiscal contracíclica."}
        },
        6: {
            "capitalist": {"defiende": "Vector ajustado con gasto público del 22% del PIB.", "cedio": "Subió su propuesta impositiva al 26% para cerrar el déficit.", "no_negocia": "Apertura exportadora."},
            "collectivist": {"defiende": "Vector ajustado con propiedad estatal del 30%.", "cedio": "Bajó el impuesto máximo al 48% para no frenar la inversión.", "no_negocia": "Piso de protección social."},
            "socdem": {"defiende": "Vector puente que sintetiza las concesiones mutuas.", "cedio": "Ajustó la regulación laboral a un punto de flexi-seguridad.", "no_negocia": "Sostenibilidad de la deuda."}
        },
        7: {
            "capitalist": {"defiende": "El modelo de consenso alcanzado.", "cedio": "Ratificó el pacto final aceptando el rol redistributivo del Estado.", "no_negocia": "Respeto a las reglas de mercado pactadas."},
            "collectivist": {"defiende": "El modelo de consenso alcanzado.", "cedio": "Aceptó la economía mixta con mayoría de iniciativa privada.", "no_negocia": "Garantías sociales adquiridas."},
            "socdem": {"defiende": "El modelo de consenso alcanzado.", "cedio": "Aceptó los compromisos fiscales de austeridad en bonanza.", "no_negocia": "La arquitectura del consenso."}
        }
    }
    stances = stances_templates.get(round_num, stances_templates[1])

    # 3. ¿Se están poniendo de acuerdo? (Medidor 0 a 100%)
    conv_score, coinciden, chocan = calculate_round_convergence_score(
        current_vectors["capitalist"],
        current_vectors["collectivist"],
        current_vectors["socdem"]
    )

    # 4. Consenso hasta ahora
    is_final_official = (round_num == 7)
    if is_final_official and session_data.get("proposal"):
        prop = session_data["proposal"]
        model_name = prop.get("model_name", "Pacto de Productividad y Cohesión")
        consensus_status_label = f"🏆 Modelo Oficial de Consenso: '{model_name}'"
        consensus_points = [
            f"**Impuestos:** Techo impositivo del {prop.get('policy_vector', {}).get('max_tax_rate', 0.35):.0%} con progresividad del {prop.get('policy_vector', {}).get('tax_progressivity', 0.60):.0%}.",
            f"**Gasto y Bienestar:** Gasto social del {prop.get('policy_vector', {}).get('public_spending_gdp', 0.25):.0%} enfocado en salud, educación e infancia.",
            f"**Economía y Empleo:** {prop.get('policy_vector', {}).get('state_ownership', 0.20):.0%} de propiedad estatal estratégica, con apertura comercial del {prop.get('policy_vector', {}).get('trade_openness', 0.75):.0%}.",
            f"**Rigor Fiscal:** Regla fiscal estricta del {prop.get('policy_vector', {}).get('fiscal_rule_strictness', 0.75):.0%} y Banco Central independiente."
        ]
    else:
        mid_vec = compute_provisional_midpoint_vector(
            current_vectors["capitalist"],
            current_vectors["collectivist"],
            current_vectors["socdem"]
        )
        consensus_status_label = "🟡 Punto Medio Provisional (Estimación matemática del sistema, aún sin nombre oficial)"
        consensus_points = [
            f"**Impuestos:** Techo sugerido de {mid_vec['max_tax_rate']:.0%} con progresividad de {mid_vec['tax_progressivity']:.0%}.",
            f"**Gasto Social:** Cobertura de ayudas sociales estimada en {mid_vec['social_transfers_coverage']:.0%}.",
            f"**Papel del Estado:** Propiedad pública provisional del {mid_vec['state_ownership']:.0%}.",
            f"**Regulación:** Protección laboral y flexibilidad en {mid_vec['labor_protection']:.0%}."
        ]

    # 5. Lo que cambió desde la ronda anterior
    if round_num == 1:
        what_changed = "Fase de apertura: se establecen las líneas rojas y los puntos de partida de cada sistema."
    else:
        prev_conv_score, _, _ = calculate_round_convergence_score(
            prev_vectors["capitalist"],
            prev_vectors["collectivist"],
            prev_vectors["socdem"]
        )
        delta = conv_score - prev_conv_score
        if delta > 0:
            what_changed = f"📈 La distancia entre los 3 agentes se redujo un {delta:.1f}%. El mayor acercamiento se dio en {coinciden[0][0]}."
        elif delta < 0:
            what_changed = f"📉 Aumentó la tensión técnica en {abs(delta):.1f}%, principalmente al debatir sobre {chocan[0][0]}."
        else:
            what_changed = f"⚖️ Los agentes mantuvieron sus posiciones mientras contrastaban los datos del simulador."

    return {
        "round_number": round_num,
        "what_happened": what_happened,
        "stances": stances,
        "convergence_pct": round(conv_score, 1),
        "coinciden": coinciden,
        "chocan": chocan,
        "consensus_status_label": consensus_status_label,
        "consensus_points": consensus_points,
        "what_changed": what_changed,
        "is_final_official": is_final_official
    }

def generate_full_debate_evolution_table(session_data: Dict[str, Any]) -> pd.DataFrame:
    """Genera la tabla histórica 'Cómo fue cambiando el acuerdo' ronda a ronda."""
    from src.app.viz.debate_adapter import _normalize_session_data
    norm_data = _normalize_session_data(session_data)
    rows = []
    rounds_count = len(norm_data.get("rounds", []))
    for r in range(1, rounds_count + 1):
        card = generate_round_summary_card(norm_data, r)
        rows.append({
            "Ronda": f"Ronda {r}",
            "Acercamiento": f"{card['convergence_pct']:.1f}%",
            "Capitalista": card["stances"]["capitalist"]["defiende"][:45] + "...",
            "Colectivista": card["stances"]["collectivist"]["defiende"][:45] + "...",
            "Socialdemócrata": card["stances"]["socdem"]["defiende"][:45] + "...",
            "Acuerdo Provisional": card["consensus_status_label"].replace("🟡 ", "").replace("🏆 ", "")[:50] + "..."
        })
    return pd.DataFrame(rows)
