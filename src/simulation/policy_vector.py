"""
Definición y Transformación del Vector de Políticas Económicas.
Mapea parámetros normalizados en [0.0, 1.0] a valores macroeconómicos y carga arquetipos validados desde YAML.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
import numpy as np
from pydantic import BaseModel, Field
from src.agents.schemas import PolicyVectorSchema

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_YAML_PATH = BASE_DIR / "config" / "economic_parameters.yaml"

class PolicyVector:
    """
    Vector de 10 dimensiones de política macroeconómica normalizadas en [0.0, 1.0].
    """
    DIMENSION_NAMES = [
        "state_ownership",            # 0: Propiedad estatal (0=0%, 1=100%)
        "max_tax_rate",               # 1: Tasa marginal máxima (0=10%, 1=80%)
        "tax_progressivity",          # 2: Progresividad impositiva (0=Flat, 1=Ultra progresivo)
        "public_spending_gdp",        # 3: Gasto público / PIB (0=10%, 1=65%)
        "social_transfers_coverage",  # 4: Transferencias y red de seguridad (0=0%, 1=Universal 100%)
        "market_regulation",          # 5: Regulación de mercados / antimonopolio (0=Min, 1=Max)
        "labor_protection",           # 6: Rigidez / protección laboral y salario min (0=Flex, 1=Rigid)
        "trade_openness",             # 7: Apertura comercial y movilidad capital (0=Autarquía, 1=Libre)
        "fiscal_rule_strictness",     # 8: Rigor de la regla fiscal (0=Discrecional, 1=Tope estricto)
        "central_bank_independence",  # 9: Independencia del Banco Central (0=Fiscal, 1=Autónomo)
    ]

    def __init__(self, values: Optional[List[float]] = None, **kwargs):
        if values is not None:
            if len(values) != 10:
                raise ValueError(f"El vector debe contener exactamente 10 valores, se recibieron {len(values)}")
            self.values = np.clip(np.array(values, dtype=np.float64), 0.0, 1.0)
        elif kwargs:
            vals = [kwargs.get(name, 0.5) for name in self.DIMENSION_NAMES]
            self.values = np.clip(np.array(vals, dtype=np.float64), 0.0, 1.0)
        else:
            self.values = np.full(10, 0.5, dtype=np.float64)

    @property
    def state_ownership(self) -> float: return float(self.values[0])
    @property
    def max_tax_rate(self) -> float: return float(self.values[1])
    @property
    def tax_progressivity(self) -> float: return float(self.values[2])
    @property
    def public_spending_gdp(self) -> float: return float(self.values[3])
    @property
    def social_transfers_coverage(self) -> float: return float(self.values[4])
    @property
    def market_regulation(self) -> float: return float(self.values[5])
    @property
    def labor_protection(self) -> float: return float(self.values[6])
    @property
    def trade_openness(self) -> float: return float(self.values[7])
    @property
    def fiscal_rule_strictness(self) -> float: return float(self.values[8])
    @property
    def central_bank_independence(self) -> float: return float(self.values[9])

    @classmethod
    def from_schema(cls, schema: PolicyVectorSchema) -> "PolicyVector":
        return cls(schema.to_array())

    def to_schema(self) -> PolicyVectorSchema:
        return PolicyVectorSchema.from_array(self.values.tolist())

    def to_dict(self) -> Dict[str, float]:
        return {name: float(self.values[i]) for i, name in enumerate(self.DIMENSION_NAMES)}

    # =========================================================================
    # Mapeos a tasas reales macroeconómicas
    # =========================================================================
    @property
    def real_state_share(self) -> float:
        """Proporción estatal del capital: 0% a 90%"""
        return float(self.values[0] * 0.90)

    @property
    def real_top_tax_rate(self) -> float:
        """Tasa impositiva máxima: 10% a 75%"""
        return float(0.10 + self.values[1] * 0.65)

    @property
    def real_tax_progressivity(self) -> float:
        """Índice Kakwani de progresividad: 0.05 a 0.50"""
        return float(0.05 + self.values[2] * 0.45)

    @property
    def real_spending_target_gdp(self) -> float:
        """Gasto público meta (% PIB): 12% a 60%"""
        return float(0.12 + self.values[3] * 0.48)

    @property
    def real_transfers_share(self) -> float:
        """Porcentaje del gasto en transferencias sociales: 10% a 70%"""
        return float(0.10 + self.values[4] * 0.60)

    @property
    def real_regulation_index(self) -> float:
        """Índice de regulación de mercados (0=desregulado, 1=muy regulado)"""
        return float(self.values[5])

    @property
    def real_labor_rigidity(self) -> float:
        """Índice de rigidez laboral / salario mínimo relativo (0 a 1)"""
        return float(self.values[6])

    @property
    def real_trade_openness(self) -> float:
        """Apertura comercial (aranceles bajos y flujo de IED): 10% a 95%"""
        return float(0.10 + self.values[7] * 0.85)

    @property
    def real_fiscal_strictness(self) -> float:
        """Rigor fiscal (tope déficit primario de 0.5% a 6.0% tolerado)"""
        return float(self.values[8])

    @property
    def real_cb_independence(self) -> float:
        """Independencia banco central (0=dominancia fiscal, 1=meta inflación estricta)"""
        return float(self.values[9])


POLICY_DIMENSIONS = PolicyVector.DIMENSION_NAMES


def load_yaml_archetypes() -> Dict[str, PolicyVector]:
    """Carga los arquetipos iniciales desde config/economic_parameters.yaml con validación Pydantic."""
    if CONFIG_YAML_PATH.exists():
        try:
            with open(CONFIG_YAML_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            arch = data.get("initial_archetypes", {})
            return {
                "capitalist": PolicyVector.from_schema(PolicyVectorSchema(**arch["capitalist"])),
                "collectivist": PolicyVector.from_schema(PolicyVectorSchema(**arch["collectivist"])),
                "socdem": PolicyVector.from_schema(PolicyVectorSchema(**arch["socdem"])),
            }
        except Exception:
            pass

    # Fallback predeterminado
    return {
        "capitalist": PolicyVector([0.05, 0.15, 0.20, 0.12, 0.15, 0.15, 0.15, 0.95, 0.90, 0.95]),
        "collectivist": PolicyVector([0.85, 0.80, 0.90, 0.85, 0.85, 0.85, 0.85, 0.35, 0.35, 0.25]),
        "socdem": PolicyVector([0.25, 0.65, 0.75, 0.65, 0.80, 0.55, 0.70, 0.85, 0.75, 0.90]),
    }

_ARCHETYPES = load_yaml_archetypes()
CAPITALIST_INITIAL_VECTOR = _ARCHETYPES["capitalist"]
COLLECTIVIST_INITIAL_VECTOR = _ARCHETYPES["collectivist"]
SOCDEM_INITIAL_VECTOR = _ARCHETYPES["socdem"]
