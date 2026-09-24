"""
Cargador de Datos Reales de Calibración (Banco Mundial / OECD / Fallback Local).
Permite calibrar los parámetros iniciales del simulador con economías reales como Colombia o Suecia.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.config import CALIBRATION_CACHE_DIR

# Perfiles económicos pre-calibrados con series históricas del Banco Mundial / OECD
DEFAULT_CALIBRATION_PROFILES = {
    "colombia": {
        "country_name": "Colombia (Emergente de Ingreso Medio)",
        "country_code": "COL",
        "initial_gdp": 100.0,
        "base_gdp_pc_usd": 7500.0,       # PIB per cápita base ~7,500 USD
        "initial_k": 210.0,
        "initial_h": 45.0,
        "initial_l": 100.0,
        "initial_tfp": 0.95,
        "initial_debt_gdp": 0.58,        # Deuda bruta / PIB aprox 58%
        "n_pop_growth": 0.009,           # Crecimiento poblacional 0.9%
        "initial_inflation": 0.055,      # Inflación 5.5%
        "initial_unemployment": 0.098,   # Desempleo 9.8%
        "baseline_gini": 0.53,           # Gini aprox 0.53
        "baseline_poverty": 0.36,        # Pobreza monetaria 36%
        "baseline_informality": 0.56,    # Informalidad laboral estructural ~56%
        "pension_coverage": 0.25,        # Cobertura pensional contributiva solo ~25%
        "state_capacity_index": 0.62,    # Índice de capacidad y ejecución institucional
        "tax_revenue_gdp": 0.19,         # Recaudo tributario actual ~19% PIB (vs 43% nórdico)
        "spending_gdp": 0.28,            # Gasto total gobierno general ~28% PIB
    },
    "nordic": {
        "country_name": "Suecia / Modelo Nórdico (Avanzada de Bienestar)",
        "country_code": "SWE",
        "initial_gdp": 160.0,
        "base_gdp_pc_usd": 58000.0,      # PIB per cápita base ~58,000 USD
        "initial_k": 320.0,
        "initial_h": 90.0,
        "initial_l": 100.0,
        "initial_tfp": 1.45,
        "initial_debt_gdp": 0.38,        # Deuda / PIB aprox 38%
        "n_pop_growth": 0.005,           # Crecimiento poblacional 0.5%
        "initial_inflation": 0.025,      # Inflación 2.5%
        "initial_unemployment": 0.068,   # Desempleo 6.8%
        "baseline_gini": 0.28,           # Gini aprox 0.28
        "baseline_poverty": 0.09,        # Pobreza relativa 9%
        "tax_revenue_gdp": 0.43,         # Recaudo tributario ~43% PIB
        "spending_gdp": 0.48,            # Gasto total ~48% PIB
    },
    "usa": {
        "country_name": "Estados Unidos (Economía Avanzada de Mercado)",
        "country_code": "USA",
        "initial_gdp": 200.0,
        "base_gdp_pc_usd": 79000.0,      # PIB per cápita base ~79,000 USD
        "initial_k": 380.0,
        "initial_h": 85.0,
        "initial_l": 100.0,
        "initial_tfp": 1.55,
        "initial_debt_gdp": 1.15,        # Deuda / PIB aprox 115%
        "n_pop_growth": 0.004,           # Crecimiento 0.4%
        "initial_inflation": 0.030,      # Inflación 3.0%
        "initial_unemployment": 0.042,   # Desempleo 4.2%
        "baseline_gini": 0.41,           # Gini aprox 0.41
        "baseline_poverty": 0.12,        # Pobreza 12%
        "tax_revenue_gdp": 0.26,         # Recaudo ~26% PIB
        "spending_gdp": 0.37,            # Gasto ~37% PIB
    }
}

def save_calibration_cache():
    """Guarda los perfiles pre-calibrados en disco."""
    for key, data in DEFAULT_CALIBRATION_PROFILES.items():
        file_path = CALIBRATION_CACHE_DIR / f"{key}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def load_calibration_profile(profile_name: str = "colombia") -> Dict[str, Any]:
    """
    Carga un perfil de calibración económico por nombre ('colombia', 'nordic', 'usa').
    """
    name = profile_name.lower().strip()
    file_path = CALIBRATION_CACHE_DIR / f"{name}.json"

    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    if name in DEFAULT_CALIBRATION_PROFILES:
        return DEFAULT_CALIBRATION_PROFILES[name]

    # Fallback por defecto a Colombia
    return DEFAULT_CALIBRATION_PROFILES["colombia"]

# Guardar caché al importar
save_calibration_cache()
