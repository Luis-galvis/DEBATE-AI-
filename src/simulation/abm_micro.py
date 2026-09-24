"""
Capa Micro Basada en Agentes (ABM) con Mesa 3.x.
Modela interacciones individuales entre Hogares heterogéneos, Firmas y Gobierno para verificar micro-fundamentos.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import mesa
from src.simulation.policy_vector import PolicyVector

class HouseholdAgent(mesa.Agent):
    """Agente hogar con dotación de habilidades heterogéneas y propensión al ahorro."""
    def __init__(self, model: mesa.Model, skill_level: float, wealth: float):
        super().__init__(model)
        self.skill_level = skill_level
        self.wealth = wealth
        self.income = 0.0
        self.consumption = 0.0
        self.employed = True

    def step(self):
        # 1. Ingreso laboral basado en habilidad, productividad de mercado y salario mínimo
        wage_rate = self.model.avg_wage * (0.5 + self.skill_level)
        min_wage = self.model.avg_wage * (0.3 + 0.4 * self.model.policy.real_labor_rigidity)

        # Probabilidad de desempleo según rigidez y choque
        unemp_prob = max(0.02, 0.05 + 0.06 * self.model.policy.real_labor_rigidity - 0.04 * self.skill_level)
        self.employed = (self.model.random.random() > unemp_prob)

        if self.employed:
            self.income = max(wage_rate, min_wage)
        else:
            # Seguro de desempleo / transferencias
            self.income = min_wage * 0.65 * self.model.policy.real_transfers_share

        # 2. Impuestos progresivos
        norm_income = max(0.1, self.income / (self.model.avg_wage * 3.0))
        tax_rate = self.model.policy.real_top_tax_rate * (norm_income ** self.model.policy.real_tax_progressivity)
        tax_paid = self.income * np.clip(tax_rate, 0.05, 0.65)
        disp_income = max(1.0, self.income - tax_paid)

        # 3. Consumo y Ahorro (los hogares de menores ingresos consumen mayor proporción)
        mpc = 0.95 - 0.40 * min(1.0, self.wealth / 200.0)
        self.consumption = disp_income * mpc
        savings = disp_income - self.consumption
        self.wealth += savings

class MicroEconomyModel(mesa.Model):
    """Modelo ABM de la economía con agentes heterogéneos y agregación microeconómica."""
    def __init__(self, policy: PolicyVector, num_households: int = 250, seed: int = 42):
        super().__init__(seed=seed)
        self.policy = policy
        self.num_households = num_households
        self.avg_wage = 20.0

        # Crear agentes hogares con distribución log-normal de habilidades
        for _ in range(num_households):
            skill = float(np.clip(self.random.lognormvariate(0.0, 0.4) / 1.5, 0.1, 2.5))
            init_wealth = float(np.clip(self.random.expovariate(0.05), 5.0, 300.0))
            HouseholdAgent(self, skill_level=skill, wealth=init_wealth)

    def step(self):
        # Avanzar agentes
        self.agents.shuffle_do("step")

    def get_distribution_metrics(self) -> Dict[str, float]:
        """Calcula el Gini de riqueza y consumo a partir de los agentes individuales."""
        wealths = np.array([a.wealth for a in self.agents], dtype=np.float64)
        wealths = np.sort(np.maximum(0.1, wealths))
        n = len(wealths)
        index = np.arange(1, n + 1)
        gini_wealth = float((2 * np.sum(index * wealths) - (n + 1) * np.sum(wealths)) / (n * np.sum(wealths)))

        incomes = np.array([a.income for a in self.agents], dtype=np.float64)
        incomes = np.sort(np.maximum(0.1, incomes))
        gini_income = float((2 * np.sum(index * incomes) - (n + 1) * np.sum(incomes)) / (n * np.sum(incomes)))

        return {
            "micro_gini_wealth": round(float(np.clip(gini_wealth, 0.0, 1.0)), 3),
            "micro_gini_income": round(float(np.clip(gini_income, 0.0, 1.0)), 3),
            "micro_avg_wealth": round(float(np.mean(wealths)), 2),
            "micro_avg_income": round(float(np.mean(incomes)), 2),
        }

def run_abm_validation(policy: PolicyVector, steps: int = 20) -> Dict[str, float]:
    """Ejecuta una validación microeconómica ABM rápida con Mesa."""
    model = MicroEconomyModel(policy=policy, num_households=200, seed=42)
    for _ in range(steps):
        model.step()
    return model.get_distribution_metrics()
