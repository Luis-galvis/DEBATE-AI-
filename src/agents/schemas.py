"""
Esquemas Pydantic para Salidas Estructuradas y Validación de Tipos
Asegura que las intervenciones de los agentes y evaluaciones del árbitro cumplan reglas estrictas.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class PolicyVectorSchema(BaseModel):
    """Vector de parámetros de política económica normalizados en [0.0, 1.0]."""
    state_ownership: float = Field(default=0.20, ge=0.0, le=1.0)
    max_tax_rate: float = Field(default=0.35, ge=0.0, le=1.0)
    tax_progressivity: float = Field(default=0.50, ge=0.0, le=1.0)
    public_spending_gdp: float = Field(default=0.28, ge=0.0, le=1.0)
    social_transfers_coverage: float = Field(default=0.40, ge=0.0, le=1.0)
    market_regulation: float = Field(default=0.45, ge=0.0, le=1.0)
    labor_protection: float = Field(default=0.45, ge=0.0, le=1.0)
    trade_openness: float = Field(default=0.70, ge=0.0, le=1.0)
    fiscal_rule_strictness: float = Field(default=0.60, ge=0.0, le=1.0)
    central_bank_independence: float = Field(default=0.85, ge=0.0, le=1.0)

    def to_array(self) -> List[float]:
        return [
            self.state_ownership,
            self.max_tax_rate,
            self.tax_progressivity,
            self.public_spending_gdp,
            self.social_transfers_coverage,
            self.market_regulation,
            self.labor_protection,
            self.trade_openness,
            self.fiscal_rule_strictness,
            self.central_bank_independence,
        ]

    @classmethod
    def from_array(cls, arr: List[float]) -> "PolicyVectorSchema":
        return cls(
            state_ownership=float(arr[0]),
            max_tax_rate=float(arr[1]),
            tax_progressivity=float(arr[2]),
            public_spending_gdp=float(arr[3]),
            social_transfers_coverage=float(arr[4]),
            market_regulation=float(arr[5]),
            labor_protection=float(arr[6]),
            trade_openness=float(arr[7]),
            fiscal_rule_strictness=float(arr[8]),
            central_bank_independence=float(arr[9]),
        )

class RefereeTurnEvaluation(BaseModel):
    """Evaluación técnica y auditoría de datos por turno de debate."""
    round_number: Optional[int] = Field(default=1)
    agent_evaluated: Optional[str] = Field(default="Debatiente")
    rigor_score: float = Field(default=8.0, ge=0.0, le=10.0)
    evidence_score: float = Field(default=8.0, ge=0.0, le=10.0)
    steelman_score: float = Field(default=8.0, ge=0.0, le=10.0)
    rebuttal_score: float = Field(default=8.0, ge=0.0, le=10.0)
    total_score: float = Field(default=8.0, ge=0.0, le=10.0)
    fact_check_passed: bool = Field(default=True)
    discrepancies: List[Any] = Field(default_factory=list)
    fallacies_detected: List[Any] = Field(default_factory=list)
    feedback: str = Field(default="Intervención evaluada con rigor técnico y soporte de evidencia.")

class DebaterTurnOutput(BaseModel):
    """Estructura esperada para la intervención de un debatiente en cada ronda."""
    agent_name: str = Field(default="Debatiente")
    round_number: int = Field(default=1)
    steelman_summary: Optional[str] = Field(default=None)
    main_argument: str = Field(default="")
    cited_simulation_data: Dict[str, Any] = Field(default_factory=dict)
    acknowledged_weaknesses: List[str] = Field(default_factory=list)
    falsifiability_condition: Optional[str] = Field(default=None)
    concessions: Optional[List[str]] = Field(default=None)
    non_negotiables: Optional[List[str]] = Field(default=None)
    updated_policy_vector: Optional[PolicyVectorSchema] = Field(default=None)

class SynthesisModelProposal(BaseModel):
    """Especificación técnica del modelo de síntesis resultante."""
    model_name: str = Field(default="Modelo de Innovación Productiva, Formalización y Flexiseguridad Adaptada (IPFA)")
    tagline: str = Field(default="Mercados dinámicos, formalización laboral progresiva, red solidaria universal y ancla fiscal contracíclica.")
    core_principles: List[str] = Field(default_factory=list)
    inherited_from_capitalist: List[str] = Field(default_factory=list)
    inherited_from_collectivist: List[str] = Field(default_factory=list)
    inherited_from_socdem: List[str] = Field(default_factory=list)
    policy_vector: Optional[PolicyVectorSchema] = Field(default=None)
    consensus_achieved: bool = Field(default=True)
    unreconciled_disagreements: List[str] = Field(default_factory=list)
    justification: str = Field(default="Solución Pareto-eficiente que optimiza el compromiso intertemporal adaptado a la estructura de Colombia.")

class RefereeAutonomousVerdict(BaseModel):
    """Dictamen autónomo e independiente del Árbitro evaluando los 3 modelos puros para toda la población."""
    chosen_model: str = Field(default="Economía Social de Mercado Mixta con Formalización y Flexiseguridad Adaptada")
    verdict_title: str = Field(default="Veredicto Autónomo del Árbitro: Superioridad de la Economía Mixta Adaptada a la Realidad Estructural")
    hayek_capitalism_flaws: List[str] = Field(default_factory=lambda: [
        "Desigualdad estructural persistente (Gini > 0.48) y marginación de la base de la pirámide sin transferencias.",
        "Trampa de informalidad y subinversión en capital humano y salud en los primeros quintiles (Q1-Q2), limitando el crecimiento potencial.",
        "Fallas de mercado severas ante externalidades ambientales (emisiones de CO2) y asimetrías de información.",
        "Alta vulnerabilidad y desprotección ciudadana ante choques sistémicos (pandemias o caídas del precio de commodities)."
    ])
    marx_communism_flaws: List[str] = Field(default_factory=lambda: [
        "Problema insuperable del cálculo económico (Mises-Hayek): incapacidad de fijar precios y cantidades sin mercado.",
        "Destrucción de incentivos al riesgo, la innovación tecnológica y el esfuerzo individual, deprimiendo la TFP.",
        "Riesgo extremo de burocratización ineficiente, concentración autoritaria y captura estatal de los medios.",
        "Déficit fiscal estructural crónico, fuga masiva de capitales y riesgo de hiperinflación."
    ])
    why_chosen_wins_for_all: Dict[str, str] = Field(default_factory=lambda: {
        "vulnerable_families": "Garantiza un piso de protección universal (salud/educación gratuitas y pilar pensional solidario no contributivo) que erradica la pobreza extrema sin desincentivar la formalización.",
        "middle_class": "Provee flexiseguridad adaptada: reduce los sobrecostos no salariales para incentivar el empleo formal, protegiendo ingresos con seguro de desempleo y reentrenamiento técnico.",
        "business_and_investors": "Mantiene el mecanismo de precios libres, apertura comercial, estabilidad macroeconómica, reglas tributarias previsibles y derechos de propiedad que incentivan la inversión privada y la innovación.",
        "the_state": "Sustenta una ampliación gradual y sólida del recaudo tributario (~28%-32% del PIB) sujeta a una regla fiscal contracíclica con fondo de estabilización de commodities que protege la solvencia soberana."
    })
    detailed_verdict_text: str = Field(default="Evaluación técnica concluyente: el libre mercado genera la riqueza y la socialdemocracia pragmática garantiza su formalización, distribución y resiliencia intertemporal sin quebrar al Estado.")

