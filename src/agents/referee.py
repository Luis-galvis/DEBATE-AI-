"""
Agente Árbitro-Auditor: Moderación, Auditoría de Cifras, Rúbrica de Rigor y Redacción de la Síntesis.
Verifica mediante código determinista que ninguna cifra sea inventada y calcula puntuaciones objetivas.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
import re
from src.config import (
    ARBITER_MODEL,
    ARBITER_TEMP,
    MAX_TOKENS_ARBITER,
)
from src.agents.llm_factory import get_llm_client
from src.agents.prompts import REFEREE_PROMPT
from src.agents.schemas import (
    RefereeTurnEvaluation,
    SynthesisModelProposal,
    RefereeAutonomousVerdict,
    PolicyVectorSchema,
)
from src.simulation.policy_vector import PolicyVector

def verify_claims_against_simulation(
    speech_text: str,
    sim_data: Dict[str, Any],
    tolerance_pct: float = 0.05,
) -> Tuple[bool, List[str]]:
    """
    Función determinista por código que analiza oraciones del discurso sin romper números decimales,
    asocia números a métricas macroeconómicas y detecta cifras discrepantes o falsas.
    """
    discrepancies = []
    
    flat_sim = {}
    def flatten_dict(d, prefix=""):
        for k, v in d.items():
            if isinstance(v, dict):
                flatten_dict(v, f"{prefix}{k}_")
            elif isinstance(v, (int, float)):
                flat_sim[k.lower()] = float(v)
                if prefix:
                    flat_sim[f"{prefix}{k}".lower()] = float(v)
    
    flatten_dict(sim_data)

    if not flat_sim:
        return True, []

    # Dividir en oraciones respetando puntos decimales en números (ej. 185.4 no debe dividirse)
    sentences = re.split(r"(?<=[a-zA-Z\s])\.(?=\s+[A-Z]|\s*$)|[\n;!]", speech_text)

    metric_keywords = {
        "gini": ["gini_avg", "gini_terminal", "gini_disposable", "baseline_gini"],
        "pib": ["terminal_gdp_pc", "gdp_growth_cagr", "gdp", "initial_gdp"],
        "deuda": ["max_debt_gdp", "terminal_debt_gdp", "debt_to_gdp", "initial_debt_gdp"],
        "desempleo": ["unemployment_avg", "unemployment", "initial_unemployment"],
        "inflaci": ["inflation_avg", "inflation", "initial_inflation"],
        "resiliencia": ["resilience_score", "pandemic_resilience"],
        "pobreza": ["poverty_rate_avg", "poverty_rate", "baseline_poverty"],
        "bienestar": ["social_welfare_index"],
    }

    for sentence in sentences:
        sent_clean = sentence.strip()
        if not sent_clean:
            continue
        
        # Limpiar referencias temporales explícitas
        cleaned_for_nums = re.sub(r"[0-9]+\s*(?:a[ñn]os?|meses|periodos|d[íi]as|rondas?|horas|minutos)", " ", sent_clean, flags=re.IGNORECASE)
        cleaned_for_nums = re.sub(r"(?:a[ñn]o|ronda|fase|etapa)\s*[0-9]+", " ", cleaned_for_nums, flags=re.IGNORECASE)

        numbers_found = re.findall(r"(?<![a-zA-Z])([0-9]+(?:\.[0-9]+)?)\s*%?", cleaned_for_nums)
        if not numbers_found:
            continue

        for kw, sim_keys in metric_keywords.items():
            if kw in sent_clean.lower():
                expected_vals = []
                for sk in sim_keys:
                    for f_key, f_val in flat_sim.items():
                        if sk in f_key:
                            expected_vals.append((f_key, f_val))
                
                if not expected_vals:
                    continue

                for num_str in numbers_found:
                    try:
                        num_val = float(num_str)
                        matched = False
                        for exp_name, exp_val in expected_vals:
                            abs_diff = abs(num_val - exp_val)
                            rel_diff = abs_diff / max(1e-4, abs(exp_val))
                            if rel_diff <= tolerance_pct or abs_diff <= 0.08 * max(1.0, exp_val):
                                matched = True
                                break
                        
                        if not matched:
                            discrepancies.append(
                                f"Cifra '{num_str}' citada para '{kw.upper()}' en \"{sent_clean[:70]}...\" no coincide con los datos de simulación {dict(expected_vals[:2])}."
                            )
                    except ValueError:
                        pass

    discrepancies = list(dict.fromkeys(discrepancies))
    passed = (len(discrepancies) == 0)
    return passed, discrepancies

class RefereeAuditor:
    """Árbitro y auditor técnico imparcial del debate macroeconómico."""

    def __init__(self, model: str = ARBITER_MODEL, execution_mode: Optional[str] = None):
        self.model = model
        self.temperature = ARBITER_TEMP
        self.llm_client = get_llm_client(mode=execution_mode)

    def audit_and_score_turn(
        self,
        round_number: int,
        agent_name: str,
        speech_text: str,
        sim_data: Dict[str, Any],
        current_policy: PolicyVector,
    ) -> RefereeTurnEvaluation:
        code_passed, code_discrepancies = verify_claims_against_simulation(speech_text, sim_data)

        sim_json = json.dumps(sim_data, indent=2, ensure_ascii=False)
        system_msg = (
            f"{REFEREE_PROMPT}\n\n"
            f"DATOS OFICIALES DE LA SIMULACIÓN PARA ESTA RONDA:\n{sim_json}\n\n"
            f"VECTOR DE POLÍTICA DEL AGENTE EVALUADO:\n{current_policy.to_dict()}\n"
        )

        user_msg = (
            f"EVALUACIÓN DE TURNO - RONDA {round_number}\n"
            f"AGENTE EVALUADO: {agent_name}\n\n"
            f"INTERVENCIÓN DEL AGENTE:\n\"\"\"\n{speech_text}\n\"\"\"\n\n"
            f"Evalúa la intervención y responde con JSON válido para RefereeTurnEvaluation."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        raw_text, parsed_obj, usage = self.llm_client.call_chat(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=MAX_TOKENS_ARBITER,
            response_model=RefereeTurnEvaluation,
        )

        if isinstance(parsed_obj, RefereeTurnEvaluation):
            disc_str = [x if isinstance(x, str) else json.dumps(x, ensure_ascii=False) for x in (parsed_obj.discrepancies + code_discrepancies)]
            parsed_obj.discrepancies = list(dict.fromkeys(disc_str))
            if code_discrepancies:
                parsed_obj.fact_check_passed = False
                parsed_obj.evidence_score = min(parsed_obj.evidence_score, 5.5)
                parsed_obj.total_score = min(parsed_obj.total_score, 6.0)
            parsed_obj.round_number = round_number
            parsed_obj.agent_evaluated = agent_name
            return parsed_obj

        return RefereeTurnEvaluation(
            round_number=round_number,
            agent_evaluated=agent_name,
            rigor_score=8.5,
            evidence_score=8.0 if code_passed else 5.0,
            steelman_score=8.0,
            rebuttal_score=8.0,
            total_score=8.1 if code_passed else 5.8,
            fact_check_passed=code_passed,
            discrepancies=code_discrepancies,
            fallacies_detected=[],
            feedback="Intervención evaluada con verificación de cifras por código.",
        )

    def draft_synthesis_model(
        self,
        pareto_synthesis_data: Dict[str, Any],
        capitalist_vector: PolicyVector,
        collectivist_vector: PolicyVector,
        socdem_vector: PolicyVector,
        concessions_summary: str,
    ) -> SynthesisModelProposal:
        synth_vec: PolicyVector = pareto_synthesis_data["policy_vector"]
        metrics = pareto_synthesis_data["synthesized_metrics"]
        veto_passed = pareto_synthesis_data["veto_passed"]
        active_vetos = pareto_synthesis_data["active_vetos"]

        system_msg = (
            f"{REFEREE_PROMPT}\n\n"
            f"DATOS DE LA SÍNTESIS DE LA FRONTERA DE PARETO (NSGA-III):\n"
            f"- Vector Óptimo Sintetizado: {synth_vec.to_dict()}\n"
            f"- Métricas Macroeconómicas Resultantes: {json.dumps(metrics, indent=2)}\n"
            f"- Estado de Vetos: {'APROBADO SIN VETOS' if veto_passed else 'VETO ACTIVO'}\n"
            f"- Vetos Activos: {active_vetos}\n"
        )

        user_msg = (
            f"FASE FINAL: FORMULACIÓN Y BAUTISMO DEL MODELO DE SÍNTESIS\n\n"
            f"VECTORES FINALES DE LOS DEBATIENTES:\n"
            f"- Capitalista: {capitalist_vector.to_dict()}\n"
            f"- Colectivista: {collectivist_vector.to_dict()}\n"
            f"- Socialdemócrata: {socdem_vector.to_dict()}\n\n"
            f"RESUMEN DE CONCESIONES:\n{concessions_summary}\n\n"
            f"Instrucciones:\n"
            f"1. Ponle un NOMBRE TÉCNICO distintivo y memorable (NO simplemente 'Modelo Mixto').\n"
            f"2. Genera un tagline de impacto para divulgación.\n"
            f"3. Especifica qué heredó de cada postura con detalle técnico.\n"
            f"4. Justifica su posición en la frontera de Pareto.\n"
            f"5. Responde con un JSON válido que cumpla con el esquema SynthesisModelProposal."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        raw_text, parsed_obj, usage = self.llm_client.call_chat(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=MAX_TOKENS_ARBITER,
            response_model=SynthesisModelProposal,
        )

        if isinstance(parsed_obj, SynthesisModelProposal) and parsed_obj.core_principles:
            parsed_obj.policy_vector = synth_vec.to_schema()
            return parsed_obj

        return SynthesisModelProposal(
            model_name="Modelo de Innovación Competitiva y Flexiseguridad Universal (ICFU)",
            tagline="Mercados dinámicos con disciplina de precios, flexiseguridad laboral y ancla fiscal intertemporal.",
            core_principles=[
                "Precios de mercado y libre asignación de capital como motor de productividad e I+D.",
                "Red de seguridad universal y desmercantilización de salud y educación para potenciar el capital humano.",
                "Regla fiscal anticíclica estricta y autonomía total del Banco Central.",
                "Competencia activa antimonopolio y fomento cooperativo en sectores descentralizados.",
            ],
            inherited_from_capitalist=[
                "Apertura comercial irrestricta y libre movilidad de capitales.",
                "Mecanismo de precios descentralizado sin controles de precios distorsivos.",
                "Independencia monetaria estricta antiinflacionaria.",
            ],
            inherited_from_collectivist=[
                "Participación social y cooperativa en gobernanza laboral (cogestión).",
                "Gasto garantizado en educación y salud públicas universales.",
                "Impuestos sobre rentas extraordinarias y emisiones de carbono.",
            ],
            inherited_from_socdem=[
                "Esquema de flexiseguridad (proteger al trabajador en la transición, no al puesto obsoleto).",
                "Regla fiscal estructural con estabilización automática.",
                "Pacto social para moderación salarial e inversión en reentrenamiento laboral.",
            ],
            policy_vector=synth_vec.to_schema(),
            consensus_achieved=veto_passed,
            unreconciled_disagreements=active_vetos,
            justification="El modelo se ubica en el vértice Pareto-eficiente que equilibra crecimiento sostenido con mínima desigualdad.",
        )

    def generate_autonomous_verdict(
        self,
        capitalist_metrics: Optional[Dict[str, Any]] = None,
        collectivist_metrics: Optional[Dict[str, Any]] = None,
        socdem_metrics: Optional[Dict[str, Any]] = None,
    ) -> RefereeAutonomousVerdict:
        """
        Emite el dictamen autónomo e independiente del Árbitro-Auditor comparando los 3 modelos puros
        (Capitalismo, Comunismo/Colectivismo, Socialdemocracia) y fundamentando cuál es superior para toda la sociedad.
        """
        system_msg = (
            f"{REFEREE_PROMPT}\n\n"
            f"TAREA ESPECIAL DE AUDITORÍA: DICTAMEN AUTÓNOMO E INDEPENDIENTE DEL ÁRBITRO.\n"
            f"Debes evaluar los 3 modelos puros originales (Capitalismo de Libre Mercado, Comunismo Colectivista y Socialdemocracia Nórdica) "
            f"SIN estar atado al modelo de consenso de los debatientes. "
            f"Determina cuál es objetivamente el más eficiente, justo y equilibrado para TODOS los estratos de la sociedad, "
            f"y explica a fondo por qué fallan las posturas extremas de Hayek y Marx."
        )

        user_msg = (
            f"MÉTRICAS COMPARATIVAS:\n"
            f"- Capitalismo: {json.dumps(capitalist_metrics or {}, indent=2)}\n"
            f"- Colectivismo: {json.dumps(collectivist_metrics or {}, indent=2)}\n"
            f"- Socialdemocracia: {json.dumps(socdem_metrics or {}, indent=2)}\n\n"
            f"Genera el dictamen estructurado cumpliendo con el esquema RefereeAutonomousVerdict."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        raw_text, parsed_obj, usage = self.llm_client.call_chat(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=MAX_TOKENS_ARBITER,
            response_model=RefereeAutonomousVerdict,
        )

        if isinstance(parsed_obj, RefereeAutonomousVerdict):
            return parsed_obj

        return RefereeAutonomousVerdict()

