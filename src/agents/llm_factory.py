"""
Fábrica de Clientes LLM para GroqCloud usando el SDK oficial de Groq.
Implementa reintentos con backoff exponencial, jitter, limitación de tasa (RPM),
caché de grabación y reproducción (Record & Replay) y validación estructurada con Pydantic.
"""

import os
import json
import time
import random
import logging
from typing import List, Dict, Any, Optional, Type, Tuple
from pydantic import BaseModel
from groq import Groq

from src.config import (
    get_groq_api_key,
    EXECUTION_MODE,
    MAX_RETRIES,
    BACKOFF_FACTOR,
    RATE_LIMIT_RPM,
    REASONING_EFFORT,
)
from src.agents.cache import LLMCache

logger = logging.getLogger(__name__)

class GroqLLMClient:
    def __init__(self, mode: Optional[str] = None):
        self.api_key = get_groq_api_key()
        self.mode = mode or EXECUTION_MODE
        self.cache = LLMCache()
        self.client = Groq(api_key=self.api_key)
        self._last_call_time = 0.0
        self._min_interval = 60.0 / max(1, RATE_LIMIT_RPM)

    def _rate_limit_wait(self):
        """Control de tasa de llamadas para evitar saturar el RPM de Groq."""
        now = time.time()
        elapsed = now - self._last_call_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_call_time = time.time()

    def call_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_tokens: int = 1024,
        response_model: Optional[Type[BaseModel]] = None,
        reasoning_effort: Optional[str] = None,
    ) -> Tuple[str, Optional[BaseModel], Dict[str, Any]]:
        """
        Ejecuta una llamada al modelo en GroqCloud con caché y reintentos automáticos.
        Retorna: (texto_plano, objeto_pydantic_si_aplica, metadata_uso)
        """
        clean_model = model.strip()

        call_params = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_model": response_model.__name__ if response_model else None,
            "reasoning_effort": reasoning_effort or REASONING_EFFORT
        }

        cache_key = LLMCache.generate_key(clean_model, messages, call_params)

        # 1. Modo Replay / Record: verificar si ya existe en la caché SQLite
        if self.mode in ("replay", "record"):
            cached = self.cache.get(cache_key)
            if cached:
                raw_text = cached["content"]
                parsed_obj = None
                if response_model:
                    try:
                        parsed_obj = response_model.model_validate_json(raw_text)
                    except Exception:
                        pass
                usage = cached.get("usage", {})
                usage["from_cache"] = True
                return raw_text, parsed_obj, usage

            # Si es replay, generamos respuesta estructurada determinista instantánea
            if self.mode == "replay":
                raw_text, parsed_obj = self._generate_offline_fallback(messages, response_model)
                usage = {
                    "prompt_tokens": 150,
                    "completion_tokens": 200,
                    "total_tokens": 350,
                    "latency_ms": 5.0,
                    "from_cache": True,
                    "model": clean_model
                }
                self.cache.set(cache_key, clean_model, messages, raw_text, usage, 5.0)
                return raw_text, parsed_obj, usage

        # 2. Ejecutar llamada real a GroqCloud con Exponential Backoff + Jitter
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self._rate_limit_wait()
                start_time = time.time()

                # Parámetros para la API de Groq
                api_kwargs: Dict[str, Any] = {
                    "model": clean_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }

                if response_model is not None:
                    api_kwargs["response_format"] = {"type": "json_object"}

                response = self.client.chat.completions.create(**api_kwargs)
                latency_ms = (time.time() - start_time) * 1000.0
                raw_text = response.choices[0].message.content or ""

                parsed_obj = None
                if response_model is not None:
                    cleaned = raw_text.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
                    elif cleaned.startswith("```"):
                        cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()

                    try:
                        parsed_obj = response_model.model_validate_json(cleaned)
                    except Exception as parse_err:
                        logger.warning(f"Error parseando Pydantic {response_model.__name__}: {parse_err}")
                        # Intentar parsear via json.loads
                        try:
                            d = json.loads(cleaned)
                            parsed_obj = response_model.model_validate(d)
                        except Exception:
                            parsed_obj = None

                usage_data = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                    "latency_ms": latency_ms,
                    "from_cache": False,
                    "model": clean_model
                }

                # Guardar en caché si estamos en modo record
                if self.mode == "record":
                    self.cache.set(
                        cache_key=cache_key,
                        model=clean_model,
                        messages=messages,
                        response_content=raw_text,
                        usage=usage_data,
                        latency_ms=latency_ms
                    )

                return raw_text, parsed_obj, usage_data

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                is_transient = any(code in err_str for code in ("429", "rate limit", "500", "503", "502", "timeout"))
                if attempt < MAX_RETRIES and is_transient:
                    jitter = random.uniform(0.1, 1.0)
                    sleep_time = (BACKOFF_FACTOR ** attempt) + jitter
                    time.sleep(sleep_time)
                else:
                    break

        raise RuntimeError(
            f"Error tras {MAX_RETRIES} intentos con Groq ({clean_model}): {type(last_error).__name__} - {str(last_error)}"
        )

    def _generate_offline_fallback(
        self,
        messages: List[Dict[str, str]],
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Tuple[str, Optional[BaseModel]]:
        """Genera una respuesta determinista offline cuando no hay API key o caché previa."""
        sys_content = messages[0].get("content", "") if messages else ""
        user_content = messages[-1].get("content", "") if len(messages) > 1 else ""

        if response_model is not None:
            model_name = response_model.__name__
            if model_name == "RefereeTurnEvaluation":
                from src.agents.schemas import RefereeTurnEvaluation
                obj = RefereeTurnEvaluation(
                    round_number=1,
                    agent_evaluated="Agente",
                    rigor_score=8.6,
                    evidence_score=8.5,
                    steelman_score=8.4,
                    rebuttal_score=8.5,
                    total_score=8.5,
                    fact_check_passed=True,
                    discrepancies=[],
                    fallacies_detected=[],
                    feedback="Intervención evaluada con coherencia matemática y anclaje a las restricciones estructurales del país.",
                )
                return obj.model_dump_json(indent=2), obj

            elif model_name == "SynthesisModelProposal":
                from src.agents.schemas import SynthesisModelProposal, PolicyVectorSchema
                obj = SynthesisModelProposal(
                    model_name="Modelo de Innovación Competitiva y Flexiseguridad Universal (ICFU)",
                    tagline="Mercados dinámicos con disciplina de precios, flexiseguridad laboral y ancla fiscal intertemporal.",
                    core_principles=[
                        "Precios de mercado y libre asignación de capital como motor de productividad e I+D.",
                        "Red de seguridad universal y desmercantilización de salud y educación para potenciar el capital humano.",
                        "Regla fiscal anticíclica estricta y autonomía total del Banco de la República.",
                        "Flexiseguridad adaptada a economías con alta informalidad laboral.",
                    ],
                    inherited_from_capitalist=[
                        "Apertura comercial internacional y libre movilidad de capitales.",
                        "Mecanismo de precios descentralizado sin distorsiones arancelarias.",
                        "Independencia monetaria estricta antiinflacionaria.",
                    ],
                    inherited_from_collectivist=[
                        "Pilar solidario pensional no contributivo para adultos mayores.",
                        "Garantía universal en educación técnica/universitaria y salud pública primaria.",
                        "Fondo soberano de estabilización de commodities.",
                    ],
                    inherited_from_socdem=[
                        "Esquema de flexiseguridad laboral con seguro de desempleo transitorio.",
                        "Regla fiscal estructural con estabilización automática contracíclica.",
                        "Pacto de formalización laboral para micro y pequeñas empresas.",
                    ],
                    policy_vector=PolicyVectorSchema(
                        state_ownership=0.20,
                        max_tax_rate=0.45,
                        tax_progressivity=0.65,
                        public_spending_gdp=0.38,
                        social_transfers_coverage=0.70,
                        trade_openness=0.85,
                        fiscal_rule_strictness=0.80,
                        central_bank_independence=0.85,
                    ),
                    consensus_achieved=True,
                    unreconciled_disagreements=[],
                    justification="El modelo se ubica en el vértice Pareto-eficiente que maximiza el producto de excedentes de Nash sin incurrir en vetos.",
                )
                return obj.model_dump_json(indent=2), obj

            elif model_name == "RefereeAutonomousVerdict":
                from src.agents.schemas import RefereeAutonomousVerdict
                obj = RefereeAutonomousVerdict()
                return obj.model_dump_json(indent=2), obj

        # Discurso libre de debatiente
        is_cap = "capitalista" in sys_content.lower()
        is_col = "colectivista" in sys_content.lower()
        is_soc = "socialdem" in sys_content.lower()

        if is_cap:
            text = (
                "Desde la perspectiva del libre mercado y la escuela de Hayek y Friedman, la prosperidad duradera nace de los derechos "
                "de propiedad seguros, el cálculo económico racional y los incentivos a la innovación. En economías con informalidad "
                "estructural como Colombia (56%), el problema raíz no es la falta de regulación, sino los sobrecostos no salariales y la "
                "asfixia tributaria sobre las microempresas. Reconozco honestamente que el mercado puro genera desigualdad en el corto plazo "
                "y desprotege a los sectores vulnerables ante crisis sistémicas, por lo que aceptamos una red de seguridad básica focalizada "
                "siempre que se preserven la libre competencia, la apertura comercial y la regla fiscal."
            )
        elif is_col:
            text = (
                "Desde el marco de la economía política y la justicia social distributiva, la economía debe subordinarse a las necesidades "
                "humanas y a la erradicación de la pobreza extrema. En Colombia, donde el 36% vive en pobreza y solo el 25% de los adultos mayores "
                "logra jubilarse, el mercado desregulado reproduce la exclusión. Exigimos un Pilar Solidario Universal no contributivo y la "
                "desmercantilización de la salud y educación. Reconozco que la planificación central rígida enfrenta el problema del cálculo "
                "económico y que la estatización excesiva puede provocar fuga de capitales, por lo cual aceptamos un sector privado dinámico "
                "en un marco de economía mixta y soberanía sobre los recursos estratégicos."
            )
        else:
            text = (
                "La socialdemocracia pragmática y la economía institucional demuestran que el verdadero dilema no es Estado vs Mercado, sino "
                "cómo combinarlos para maximizar el bienestar colectivo. No podemos trasplantar ciegamente el modelo nórdico sin considerar "
                "que Colombia recauda el 19% del PIB frente al 43% escandinavo. Por ello, proponemos una Flexiseguridad secuenciada: facilitar "
                "la formalización laboral de las MiPyMEs, financiar salud y educación con impuestos progresivos a las rentas del 1% superior, "
                "y blindar la estabilidad con un Banco Central autónomo y un Fondo de Estabilización de Commodities anticíclico."
            )

        return text, None

# Instancia singleton
_global_client: Optional[GroqLLMClient] = None

def get_llm_client(mode: Optional[str] = None) -> GroqLLMClient:
    global _global_client
    if _global_client is None or mode is not None:
        _global_client = GroqLLMClient(mode=mode)
    return _global_client
