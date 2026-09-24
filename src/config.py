"""
Módulo de Configuración Global del Sistema
Carga segura de variables de entorno, modelos de Groq, rutas y parámetros de simulación.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables desde .env en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# ==========================================
# SEGURIDAD Y CREDENCIALES
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

def get_groq_api_key() -> str:
    """Retorna la clave de Groq sin exponerla en logs."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY no encontrada. Asegúrate de configurar tu archivo .env en la raíz del proyecto."
        )
    return GROQ_API_KEY

def is_groq_configured() -> bool:
    """Verifica si la API key está disponible."""
    return bool(GROQ_API_KEY)

# ==========================================
# CONFIGURACIÓN DE MODELOS GROQ
# ==========================================
DEBATER_MODEL = os.getenv("DEBATER_MODEL", "openai/gpt-oss-120b")
ARBITER_MODEL = os.getenv("ARBITER_MODEL", "openai/gpt-oss-120b")
FAST_MODEL = os.getenv("FAST_MODEL", "openai/gpt-oss-20b")
SECOND_OPINION_MODEL = os.getenv("SECOND_OPINION_MODEL", "qwen/qwen3.8-27b")

# Temperaturas
DEBATER_CAPITALIST_TEMP = float(os.getenv("DEBATER_CAPITALIST_TEMP", "0.65"))
DEBATER_COLLECTIVIST_TEMP = float(os.getenv("DEBATER_COLLECTIVIST_TEMP", "0.65"))
DEBATER_SOCDEM_TEMP = float(os.getenv("DEBATER_SOCDEM_TEMP", "0.60"))
ARBITER_TEMP = float(os.getenv("ARBITER_TEMP", "0.10"))
FAST_TEMP = float(os.getenv("FAST_TEMP", "0.20"))

# Reasoning Effort (si el modelo lo soporta)
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "medium")

# Presupuestos de tokens y Rate Limiting
MAX_TOKENS_DEBATER = int(os.getenv("MAX_TOKENS_DEBATER", "1024"))
MAX_TOKENS_ARBITER = int(os.getenv("MAX_TOKENS_ARBITER", "2048"))
MAX_TOKENS_FAST = int(os.getenv("MAX_TOKENS_FAST", "512"))
RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "60"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "1.5"))

# ==========================================
# MODOS DE EJECUCIÓN Y CACHÉ
# ==========================================
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "record").lower()  # 'live', 'record', 'replay'
CACHE_DB_PATH = Path(os.getenv("CACHE_DB_PATH", str(BASE_DIR / "outputs" / "llm_cache.sqlite")))

# ==========================================
# RUTAS DE DATOS Y SALIDAS
# ==========================================
OUTPUTS_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"
CALIBRATION_CACHE_DIR = DATA_DIR / "calibration_cache"

# Asegurar directorios
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
CALIBRATION_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# SEMILLA ALEATORIA PARA REPRODUCIBILIDAD
# ==========================================
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
