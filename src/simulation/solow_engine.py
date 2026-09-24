"""
Motor Macroeconómico Determinista Continuo (Solow Ampliado con Capital Humano y Dinámica Fiscal).
Calcula la evolución de la economía a 30 años garantizando el cierre de identidades contables: Y = C + I + G + NX.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from src.simulation.policy_vector import PolicyVector

class MacroEconomy:
    """
    Simulador macroeconómico dinámico para una trayectoria de T años (default 30 años).
    """

    def __init__(
        self,
        policy: PolicyVector,
        calibration: Optional[Dict[str, Any]] = None,
        years: int = 30,
        dt: float = 1.0,
    ):
        self.policy = policy
        self.years = years
        self.dt = dt
        self.calib = self._default_calibration()
        if calibration:
            self.calib.update(calibration)

        # Elasticidades de la función de producción Cobb-Douglas ampliada
        self.alpha = float(self.calib.get("alpha", 0.30))  # Capital físico
        self.beta = float(self.calib.get("beta", 0.25))   # Capital humano
        self.gamma_l = 1.0 - self.alpha - self.beta       # Trabajo (0.45)

        # Tasas de depreciación y parámetros estructurales
        self.delta_k = float(self.calib.get("delta_k", 0.05))   # Depreciación K físico
        self.delta_h = float(self.calib.get("delta_h", 0.02))   # Depreciación K humano
        self.r_world = float(self.calib.get("r_world", 0.035))  # Tasa de interés global

        # Quintiles de población: propensiones marginales a consumir (MPC)
        self.mpc_quintiles = np.array([0.96, 0.88, 0.78, 0.68, 0.52], dtype=np.float64)

    @staticmethod
    def _default_calibration() -> Dict[str, Any]:
        """Calibración base tipo economía emergente / media."""
        return {
            "country_name": "Economía de Referencia (Emergente Media)",
            "initial_gdp": 100.0,
            "base_gdp_pc_usd": 7500.0,
            "initial_k": 220.0,
            "initial_h": 50.0,
            "initial_l": 100.0,
            "initial_tfp": 1.0,
            "initial_debt_gdp": 0.55,
            "n_pop_growth": 0.008,
            "initial_inflation": 0.04,
            "initial_unemployment": 0.08,
        }

    def simulate(
        self,
        shock_series: Optional[Dict[str, np.ndarray]] = None,
    ) -> Dict[str, np.ndarray]:
        """
        Ejecuta la simulación determinista año a año a lo largo de T periodos.
        """
        T = self.years
        shocks = shock_series or {}

        # 1. Vectores de choque exógeno (longitud T)
        shock_tfp = shocks.get("tfp", np.zeros(T))
        shock_demand = shocks.get("demand", np.zeros(T))
        shock_spread = shocks.get("spread", np.zeros(T))
        shock_labor = shocks.get("labor", np.zeros(T))
        shock_terms_trade = shocks.get("terms_trade", np.zeros(T))
        shock_pandemic = shocks.get("health_crisis", np.zeros(T))

        # 2. Inicialización de arrays de resultados
        gdp = np.zeros(T)
        gdp_per_capita = np.zeros(T)
        tfp = np.zeros(T)
        k_stock = np.zeros(T)
        h_stock = np.zeros(T)
        labor_force = np.zeros(T)

        consumption = np.zeros(T)
        investment = np.zeros(T)
        public_spending = np.zeros(T)
        net_exports = np.zeros(T)

        tax_revenue = np.zeros(T)
        transfers = np.zeros(T)
        primary_balance = np.zeros(T)
        debt_stock = np.zeros(T)
        debt_to_gdp = np.zeros(T)
        sovereign_rate = np.zeros(T)

        gini_market = np.zeros(T)
        gini_disposable = np.zeros(T)
        poverty_rate = np.zeros(T)
        unemployment = np.zeros(T)
        informality = np.zeros(T)
        inflation = np.zeros(T)

        rd_spending = np.zeros(T)
        life_expectancy = np.zeros(T)
        economic_freedom = np.zeros(T)
        co2_emissions = np.zeros(T)

        # Estado inicial
        K = float(self.calib["initial_k"])
        H = float(self.calib["initial_h"])
        L = float(self.calib["initial_l"])
        A = float(self.calib["initial_tfp"])
        D = float(self.calib["initial_gdp"]) * float(self.calib["initial_debt_gdp"])

        p_state = self.policy.real_state_share
        p_tax_top = self.policy.real_top_tax_rate
        p_tax_prog = self.policy.real_tax_progressivity
        p_gov_gdp = self.policy.real_spending_target_gdp
        p_transfers = self.policy.real_transfers_share
        p_reg = self.policy.real_regulation_index
        p_labor_rig = self.policy.real_labor_rigidity
        p_trade = self.policy.real_trade_openness
        p_fisc_strict = self.policy.real_fiscal_strictness
        p_cb_indep = self.policy.real_cb_independence

        # 3. Bucle temporal año a año
        for t in range(T):
            pop_growth = self.calib["n_pop_growth"] + shock_labor[t]
            L = L * (1.0 + pop_growth)
            labor_force[t] = L

            nairu = 0.045 + 0.055 * p_labor_rig + 0.02 * p_reg
            u_t = np.clip(nairu - 0.15 * shock_demand[t] + 0.08 * shock_pandemic[t], 0.02, 0.28)
            unemployment[t] = u_t

            # Dinámica de informalidad laboral (Colombia: base ~56%)
            base_inf = float(self.calib.get("baseline_informality", 0.56 if "colombia" in str(self.calib.get("country_name", "")).lower() else 0.10))
            h_gain = (H / max(1.0, float(self.calib.get("initial_h", 45.0)))) - 1.0
            inf_t = np.clip(base_inf + 0.14 * p_labor_rig + 0.08 * p_tax_top - 0.10 * p_trade - 0.06 * h_gain, 0.04, 0.75)
            informality[t] = inf_t

            L_eff = L * (1.0 - u_t)
            A_eff = A * (1.0 + shock_tfp[t] + 0.05 * shock_terms_trade[t])
            tfp[t] = A_eff
            k_stock[t] = K
            h_stock[t] = H

            Y_t = A_eff * (K ** self.alpha) * (H ** self.beta) * (L_eff ** self.gamma_l)
            Y_t = max(10.0, Y_t * (1.0 + shock_demand[t]))
            gdp[t] = Y_t
            base_pc = float(self.calib.get("base_gdp_pc_usd", 7500.0))
            gdp_per_capita[t] = (Y_t / max(1.0, L)) * base_pc

            G_t = Y_t * p_gov_gdp * (1.0 + 0.10 * shock_pandemic[t])
            public_spending[t] = G_t

            laffer_penalty = max(0.0, (p_tax_top - 0.52) * 0.35)
            effective_tax_rate = (0.08 + 0.65 * p_tax_top) * (1.0 - laffer_penalty)
            T_t = Y_t * effective_tax_rate
            tax_revenue[t] = T_t

            Tr_t = G_t * p_transfers * (1.0 + 0.15 * shock_pandemic[t])
            transfers[t] = Tr_t

            prim_bal = T_t - G_t - Tr_t
            primary_balance[t] = prim_bal

            d_ratio = float(np.clip(D / max(1.0, Y_t), 0.0, 5.0))
            debt_to_gdp[t] = d_ratio

            risk_spread = (
                max(0.0, (d_ratio - 0.60) * 0.06)
                + (1.0 - p_fisc_strict) * 0.02
                + (1.0 - p_cb_indep) * 0.025
                + shock_spread[t]
            )
            r_sovereign = float(np.clip(self.r_world + max(0.0, risk_spread), 0.01, 0.25))
            sovereign_rate[t] = r_sovereign

            fiscal_correction = 0.0
            if d_ratio > 0.70 and p_fisc_strict > 0.50:
                fiscal_correction = (d_ratio - 0.70) * Y_t * 0.15 * p_fisc_strict

            next_D = D * (1.0 + r_sovereign) - (prim_bal + fiscal_correction)
            D = float(np.clip(next_D, 0.0, 10.0 * Y_t))
            debt_stock[t] = D

            expected_inf = 0.025 + (1.0 - p_cb_indep) * 0.06
            inf_t = expected_inf - 0.35 * (u_t - nairu) + 0.03 * shock_terms_trade[t]
            if d_ratio > 1.10 and p_cb_indep < 0.40:
                inf_t += 0.05 * (d_ratio - 1.10)
            inflation[t] = float(np.clip(inf_t, 0.005, 0.40))

            base_shares = np.array([0.04, 0.09, 0.14, 0.22, 0.51], dtype=np.float64)
            market_equalization = 0.08 * p_state + 0.06 * p_labor_rig
            market_shares = base_shares + np.array([1, 1, 0.5, -0.5, -2]) * (market_equalization / 2.0)
            market_shares = np.clip(market_shares, 0.02, 0.65)
            market_shares = market_shares / np.sum(market_shares)

            market_income = market_shares * Y_t
            tax_incidence = np.array([0.02, 0.06, 0.14, 0.26, 0.52]) * (1.0 + p_tax_prog * 0.3)
            tax_incidence = tax_incidence / np.sum(tax_incidence)
            taxes_paid = tax_incidence * T_t

            transfer_incidence = np.array([0.45, 0.30, 0.15, 0.08, 0.02]) * (1.0 - p_transfers * 0.2) + (p_transfers * 0.2) * 0.20
            transfer_incidence = transfer_incidence / np.sum(transfer_incidence)
            transfers_received = transfer_incidence * Tr_t

            disp_income = market_income - taxes_paid + transfers_received
            disp_income = np.clip(disp_income, 0.01 * Y_t, 0.80 * Y_t)
            disp_shares = disp_income / np.sum(disp_income)

            cum_income_disp = np.concatenate([[0.0], np.cumsum(disp_shares)])
            gini_disp = 1.0 - 2.0 * np.sum(0.5 * (cum_income_disp[:-1] + cum_income_disp[1:]) * 0.2)
            gini_disposable[t] = float(np.clip(gini_disp, 0.15, 0.70))

            poverty_rate[t] = float(np.clip(0.40 * gini_disp - 0.15 * p_transfers + 0.05 * u_t, 0.02, 0.50))

            c_quintiles = disp_income * self.mpc_quintiles
            C_t = float(np.sum(c_quintiles))
            consumption[t] = C_t

            priv_inv_incentive = (1.0 - 0.40 * p_tax_top) * (0.8 + 0.4 * p_trade) * (1.0 - 0.25 * p_reg)
            priv_savings = float(np.sum(disp_income * (1.0 - self.mpc_quintiles)))
            I_private = max(0.05 * Y_t, priv_savings * np.clip(priv_inv_incentive, 0.4, 1.5))

            I_public = G_t * (0.15 + 0.15 * p_state)
            I_t = I_private + I_public
            investment[t] = I_t

            # Cierre exacto Y = C + I + G + NX
            NX_t = Y_t - (C_t + I_t + G_t)
            net_exports[t] = NX_t

            rd_ratio = 0.008 + 0.035 * (1.0 - p_state) * p_trade + 0.020 * (G_t / Y_t) * 0.10
            rd_spending[t] = rd_ratio

            tfp_growth = 0.010 + 0.35 * rd_ratio + 0.008 * p_trade - 0.012 * (p_reg ** 2)
            A = A * (1.0 + tfp_growth)
            K = max(10.0, K * (1.0 - self.delta_k) + I_t)

            edu_health_spending = G_t * (0.30 + 0.30 * self.policy.values[4])
            H = max(5.0, H * (1.0 - self.delta_h) + 0.18 * (edu_health_spending ** 0.55))

            life_expectancy[t] = 68.0 + 12.0 * (1.0 - poverty_rate[t]) + 4.0 * (edu_health_spending / Y_t)
            economic_freedom[t] = 10.0 * (
                0.25 * (1.0 - p_state)
                + 0.20 * (1.0 - p_tax_top)
                + 0.20 * p_trade
                + 0.20 * (1.0 - p_reg)
                + 0.15 * p_cb_indep
            )
            co2_emissions[t] = (Y_t / 100.0) * (1.4 - 0.60 * p_reg - 0.30 * (G_t / Y_t))

        return {
            "gdp": gdp,
            "gdp_per_capita": gdp_per_capita,
            "tfp": tfp,
            "k_stock": k_stock,
            "h_stock": h_stock,
            "labor_force": labor_force,
            "consumption": consumption,
            "investment": investment,
            "public_spending": public_spending,
            "net_exports": net_exports,
            "tax_revenue": tax_revenue,
            "transfers": transfers,
            "primary_balance": primary_balance,
            "debt_stock": debt_stock,
            "debt_to_gdp": debt_to_gdp,
            "sovereign_rate": sovereign_rate,
            "gini_market": gini_market,
            "gini_disposable": gini_disposable,
            "poverty_rate": poverty_rate,
            "unemployment": unemployment,
            "informality_rate": informality,
            "inflation": inflation,
            "rd_spending": rd_spending,
            "life_expectancy": life_expectancy,
            "economic_freedom": economic_freedom,
            "co2_emissions": co2_emissions,
        }
