"""
Catálogo Unificado de Métricas Macroeconómicas, Sociales, Fiscales y Ambientales.
Define las fórmulas, unidades, dirección de optimización (↑ / ↓) y procedencia en el motor.
"""

from typing import Dict, Any, List

METRICS_CATALOG: Dict[str, Dict[str, Any]] = {
    # 1. Crecimiento y Producción
    "gdp_growth_cagr": {
        "name": "Crecimiento PIB (CAGR 30a)",
        "category": "Crecimiento y Producción",
        "unit": "% anual",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Tasa de crecimiento anual compuesta del PIB real a lo largo del horizonte de 30 años.",
        "formula": "((Y_30 / Y_0)^(1/30) - 1) * 100",
        "source": "SolowSwanEngine (Y_t)",
    },
    "terminal_gdp_pc": {
        "name": "PIB per cápita Terminal",
        "category": "Crecimiento y Producción",
        "unit": "USD / hab",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Nivel de ingreso por habitante alcanzado en el año 30 de simulación.",
        "formula": "Y_30 / L_30",
        "source": "SolowSwanEngine (gdp_per_capita)",
    },
    "labor_productivity": {
        "name": "Productividad Laboral",
        "category": "Crecimiento y Producción",
        "unit": "USD / trabajador",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Producto interior bruto generado por cada trabajador ocupado.",
        "formula": "Y_t / (L_t * (1 - u_t))",
        "source": "SolowSwanEngine (productivity)",
    },
    "investment_gdp": {
        "name": "Tasa de Inversión / PIB",
        "category": "Crecimiento y Producción",
        "unit": "% del PIB",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Porcentaje del producto nacional destinado a formación bruta de capital fijo.",
        "formula": "(I_t / Y_t) * 100",
        "source": "SolowSwanEngine (investment)",
    },
    "rd_gdp_avg": {
        "name": "Inversión en I+D / PIB",
        "category": "Crecimiento y Producción",
        "unit": "% del PIB",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Gasto promedio en investigación, desarrollo tecnológico e innovación.",
        "formula": "mean(I_RD / Y) * 100",
        "source": "SolowSwanEngine (rd_spending)",
    },

    # 2. Desigualdad y Pobreza
    "gini_avg": {
        "name": "Coeficiente de Gini Promedio",
        "category": "Desigualdad y Pobreza",
        "unit": "Índice [0 - 1]",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Medida de concentración del ingreso disponible tras transferencias e impuestos progresivos.",
        "formula": "mean(Gini_disposable)",
        "source": "SolowSwanEngine (gini_disposable)",
    },
    "gini_terminal": {
        "name": "Gini Terminal (Año 30)",
        "category": "Desigualdad y Pobreza",
        "unit": "Índice [0 - 1]",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Coeficiente de desigualdad alcanzado al final de la transición de 30 años.",
        "formula": "Gini_disposable[30]",
        "source": "SolowSwanEngine (gini_disposable)",
    },
    "poverty_rate_avg": {
        "name": "Tasa de Pobreza Promedio",
        "category": "Desigualdad y Pobreza",
        "unit": "% población",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Porcentaje de la población con ingreso disponible inferior a la línea de pobreza relativa.",
        "formula": "mean(Poverty_t) * 100",
        "source": "SolowSwanEngine (poverty_rate)",
    },
    "q1_income_share": {
        "name": "Participación Quintil 1 (20% más pobre)",
        "category": "Desigualdad y Pobreza",
        "unit": "% del ingreso total",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Porcentaje del ingreso nacional disponible acumulado por el 20% de menores recursos.",
        "formula": "(Y_d,Q1 / Y_d,total) * 100",
        "source": "SolowSwanEngine (quintiles)",
    },
    "q5_income_share": {
        "name": "Participación Quintil 5 (20% más rico)",
        "category": "Desigualdad y Pobreza",
        "unit": "% del ingreso total",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Porcentaje del ingreso nacional disponible concentrado en el quintil superior.",
        "formula": "(Y_d,Q5 / Y_d,total) * 100",
        "source": "SolowSwanEngine (quintiles)",
    },

    # 3. Trabajo y Empleo
    "unemployment_avg": {
        "name": "Tasa de Desempleo Promedio",
        "category": "Trabajo y Empleo",
        "unit": "% fuerza laboral",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Porcentaje promedio de la fuerza laboral que busca activamente empleo sin encontrarlo.",
        "formula": "mean(u_t) * 100",
        "source": "SolowSwanEngine (unemployment)",
    },
    "labor_share": {
        "name": "Participación del Trabajo en el Ingreso",
        "category": "Trabajo y Empleo",
        "unit": "% del PIB",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Porcentaje del PIB remunerado como salarios e ingresos laborales de los trabajadores.",
        "formula": "(W_t * L_eff / Y_t) * 100",
        "source": "SolowSwanEngine (labor_share)",
    },
    "real_wage_index": {
        "name": "Índice de Salario Real",
        "category": "Trabajo y Empleo",
        "unit": "Base 100",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Evolución del poder adquisitivo del salario medio ajustado por inflación.",
        "formula": "(W_30 / P_30) / (W_0 / P_0) * 100",
        "source": "SolowSwanEngine (real_wage)",
    },

    # 4. Precios y Finanzas Públicas
    "tax_revenue_gdp_avg": {
        "name": "Recaudo Tributario / PIB Promedio",
        "category": "Precios y Finanzas",
        "unit": "% del PIB",
        "direction": "↑ equilibrado",
        "better_is_higher": True,
        "description": "Ingresos tributarios efectivos recaudados por el Estado como porcentaje del PIB.",
        "formula": "mean(TaxRevenue_t / Y_t) * 100",
        "source": "SolowSwanEngine (tax_revenue)",
    },
    "tax_revenue_terminal": {
        "name": "Recaudo Tributario Terminal",
        "category": "Precios y Finanzas",
        "unit": "% del PIB",
        "direction": "↑ equilibrado",
        "better_is_higher": True,
        "description": "Nivel de recaudación fiscal sobre el PIB alcanzado al final del periodo.",
        "formula": "(TaxRevenue_30 / Y_30) * 100",
        "source": "SolowSwanEngine (tax_revenue)",
    },
    "inflation_avg": {
        "name": "Inflación Promedio",
        "category": "Precios y Finanzas",
        "unit": "% anual",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Tasa promedio de variación del índice general de precios.",
        "formula": "mean(pi_t) * 100",
        "source": "SolowSwanEngine (inflation)",
    },
    "terminal_debt_gdp": {
        "name": "Deuda Pública / PIB Terminal",
        "category": "Precios y Finanzas",
        "unit": "% del PIB",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Saldo de la deuda pública neta como porcentaje del producto al cierre del horizonte.",
        "formula": "(D_30 / Y_30) * 100",
        "source": "SolowSwanEngine (debt_to_gdp)",
    },
    "max_debt_gdp": {
        "name": "Deuda Pública / PIB Máxima",
        "category": "Precios y Finanzas",
        "unit": "% del PIB",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Pico máximo de endeudamiento público registrado en los 30 periodos.",
        "formula": "max(D_t / Y_t) * 100",
        "source": "SolowSwanEngine (debt_to_gdp)",
    },
    "fiscal_sustainability_score": {
        "name": "Sostenibilidad Fiscal",
        "category": "Precios y Finanzas",
        "unit": "Puntos [0 - 100]",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Índice de solvencia intertemporal y margen contra crisis de deuda soberana.",
        "formula": "100 - (0.5 * Debt_30 + 1.5 * max(0, Debt_30 - 75))",
        "source": "metrics.py (fiscal_sustainability)",
    },

    # 5. Bienestar Social y Servicios
    "life_expectancy_avg": {
        "name": "Esperanza de Vida Media",
        "category": "Bienestar y Servicios",
        "unit": "Años",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Años promedio de vida estimados en función del capital humano y gasto en salud pública.",
        "formula": "mean(LifeExpectancy_t)",
        "source": "SolowSwanEngine (life_expectancy)",
    },
    "social_welfare_index": {
        "name": "Índice de Bienestar Social Integral",
        "category": "Bienestar y Servicios",
        "unit": "Puntos [0 - 100]",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Índice sintético que combina Crecimiento, Igualdad, Salud, Libertades y Sostenibilidad.",
        "formula": "0.25*NormGDP + 0.25*NormGini + 0.20*NormLife + 0.15*NormFree + 0.15*NormFisc",
        "source": "metrics.py (social_welfare_index)",
    },

    # 6. Resiliencia ante Choques
    "max_drawdown": {
        "name": "Caída Máxima ante Choques (Drawdown)",
        "category": "Resiliencia ante Choques",
        "unit": "% caída PIB",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Máxima contracción interanual del PIB observada durante los escenarios de estrés.",
        "formula": "abs(min(diff(Y)/Y)) * 100",
        "source": "metrics.py (max_drawdown)",
    },
    "resilience_score": {
        "name": "Índice de Resiliencia",
        "category": "Resiliencia ante Choques",
        "unit": "Puntos [0 - 100]",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Capacidad de la estructura macroeconómica de absorber perturbaciones sin daño permanente.",
        "formula": "100 - (3.5 * Drawdown + 4.0 * Volatilidad)",
        "source": "metrics.py (resilience_score)",
    },

    # 7. Ambiente y Libertades
    "total_co2": {
        "name": "Emisiones Acumuladas de CO2",
        "category": "Ambiente y Libertades",
        "unit": "Mt CO2 eq",
        "direction": "↓ mejor",
        "better_is_higher": False,
        "description": "Emisiones totales acumuladas de gases de efecto invernadero en 30 años.",
        "formula": "sum(CO2_t)",
        "source": "SolowSwanEngine (co2_emissions)",
    },
    "economic_freedom_avg": {
        "name": "Índice de Libertad Económica (Proxy)",
        "category": "Ambiente y Libertades",
        "unit": "Puntos [0 - 10]",
        "direction": "↑ mejor",
        "better_is_higher": True,
        "description": "Indicador sintético de apertura de mercados, derechos de propiedad y baja coerción regulatoria.",
        "formula": "mean(EconomicFreedom_t)",
        "source": "SolowSwanEngine (economic_freedom)",
    },
}

COLOR_PALETTE = {
    "capitalist": "#E53E3E",   # Rojo carmesí / Terracota
    "collectivist": "#DD6B20", # Naranja óxido / Ámbar
    "socdem": "#3182CE",       # Azul zafiro
    "referee": "#805AD5",      # Púrpura amatista
    "consensus": "#D69E2E",    # Dorado brillante
}

SYSTEM_LABELS = {
    "capitalist": "El Capitalista (Libre Mercado)",
    "collectivist": "El Colectivista (Planificación Democrática)",
    "socdem": "El Socialdemócrata (Economía Mixta Nórdica)",
    "consensus": "Consenso Sintetizado (Punto Medio NSGA-III)",
}
