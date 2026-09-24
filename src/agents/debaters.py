"""
Clases de los Tres Agentes Debatientes: Capitalista, Colectivista y Socialdemócrata.
Manejan la memoria contextual, compresión de rondas previas y la emisión de argumentos rigurosos.
"""

from typing import Dict, Any, List, Optional
import json
from src.config import (
    DEBATER_MODEL,
    DEBATER_CAPITALIST_TEMP,
    DEBATER_COLLECTIVIST_TEMP,
    DEBATER_SOCDEM_TEMP,
    MAX_TOKENS_DEBATER,
)
from src.agents.llm_factory import get_llm_client
from src.agents.prompts import (
    CAPITALIST_PROMPT,
    COLLECTIVIST_PROMPT,
    SOCDEM_PROMPT,
)
from src.agents.schemas import DebaterTurnOutput, PolicyVectorSchema
from src.simulation.policy_vector import (
    PolicyVector,
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)

class BaseDebater:
    """Clase base para los agentes debatientes con memoria comprimida y reglas éticas."""

    def __init__(
        self,
        name: str,
        role_prompt: str,
        initial_vector: PolicyVector,
        temperature: float = 0.65,
        model: str = DEBATER_MODEL,
        execution_mode: Optional[str] = None,
    ):
        self.name = name
        self.role_prompt = role_prompt
        self.current_vector = initial_vector
        self.temperature = temperature
        self.model = model
        self.llm_client = get_llm_client(mode=execution_mode)

    def generate_turn(
        self,
        round_number: int,
        round_title: str,
        round_instruction: str,
        sim_data: Dict[str, Any],
        context_summary: str,
        response_model: Optional[Any] = None,
    ) -> Tuple_Turn:
        """
        Genera el discurso/intervención técnica del agente para la ronda actual.
        """
        # Preparar contexto comprimido de simulación para evitar alucinaciones
        sim_context_str = json.dumps(sim_data, indent=2, ensure_ascii=False)

        system_msg = (
            f"{self.role_prompt}\n\n"
            f"DATOS OFICIALES DE LA SIMULACIÓN PARA ESTA RONDA:\n{sim_context_str}\n\n"
            f"VECTORES DE POLÍTICA ACTUALES:\n{self.current_vector.to_dict()}\n"
        )

        user_msg = (
            f"RONDA {round_number}: {round_title.upper()}\n"
            f"RESUMEN DEL DEBATE HASTA AHORA:\n{context_summary}\n\n"
            f"INSTRUCCIONES ESPECÍFICAS DE ESTA RONDA:\n{round_instruction}\n\n"
            f"Recuerda cumplir las 6 reglas obligatorias (Steelman, Cero datos inventados, 2 debilidades, falsabilidad)."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        raw_text, parsed_obj, usage = self.llm_client.call_chat(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=MAX_TOKENS_DEBATER,
            response_model=response_model,
        )

        return raw_text, parsed_obj, usage

class CapitalistDebater(BaseDebater):
    def __init__(self, model: str = DEBATER_MODEL, execution_mode: Optional[str] = None):
        super().__init__(
            name="El Capitalista",
            role_prompt=CAPITALIST_PROMPT,
            initial_vector=CAPITALIST_INITIAL_VECTOR,
            temperature=DEBATER_CAPITALIST_TEMP,
            model=model,
            execution_mode=execution_mode,
        )

class CollectivistDebater(BaseDebater):
    def __init__(self, model: str = DEBATER_MODEL, execution_mode: Optional[str] = None):
        super().__init__(
            name="El Colectivista",
            role_prompt=COLLECTIVIST_PROMPT,
            initial_vector=COLLECTIVIST_INITIAL_VECTOR,
            temperature=DEBATER_COLLECTIVIST_TEMP,
            model=model,
            execution_mode=execution_mode,
        )

class SocdemDebater(BaseDebater):
    def __init__(self, model: str = DEBATER_MODEL, execution_mode: Optional[str] = None):
        super().__init__(
            name="El Socialdemócrata",
            role_prompt=SOCDEM_PROMPT,
            initial_vector=SOCDEM_INITIAL_VECTOR,
            temperature=DEBATER_SOCDEM_TEMP,
            model=model,
            execution_mode=execution_mode,
        )

# Type alias helper
Tuple_Turn = Any
