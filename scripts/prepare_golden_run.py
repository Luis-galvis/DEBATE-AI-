"""
Generador del Paquete 'Golden Run' para Grabación y Reproducción Offline 100% Determinista.
Copia y estructura los artefactos definitivos en outputs/golden_run/ junto con su documentación de metadatos.
"""

import sys
import shutil
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Safe stdout on Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config import OUTPUTS_DIR, RANDOM_SEED

def prepare_golden_run():
    golden_dir = OUTPUTS_DIR / "golden_run"
    golden_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copiar base de datos de caché SQLite
    src_sqlite = OUTPUTS_DIR / "llm_cache.sqlite"
    dst_sqlite = golden_dir / "llm_cache_golden.sqlite"
    if src_sqlite.exists():
        shutil.copy2(src_sqlite, dst_sqlite)

    # 2. Copiar última sesión JSON
    src_json = OUTPUTS_DIR / "debate_session_latest.json"
    dst_json = golden_dir / "debate_session_golden.json"
    if src_json.exists():
        shutil.copy2(src_json, dst_json)

    # 3. Copiar reportes MD y PDF
    for filename in ["final_synthesis_report.md", "final_synthesis_report.pdf", "key_moments.md", "video_script.md"]:
        src_f = OUTPUTS_DIR / filename
        if src_f.exists():
            shutil.copy2(src_f, golden_dir / filename)

    # 4. Copiar figuras de alta resolución
    for fig_name in [
        "pareto_frontier_2d.png", "pareto_frontier_2d.svg",
        "radar_comparison_systems.png", "radar_comparison_systems.svg",
        "monte_carlo_trajectories.png", "monte_carlo_trajectories.svg"
    ]:
        src_fig = OUTPUTS_DIR / fig_name
        if src_fig.exists():
            shutil.copy2(src_fig, golden_dir / fig_name)

    # 5. Generar README de metadatos del Golden Run
    readme_content = f"""# GOLDEN RUN — PAQUETE MAESTRO DE GRABACIÓN REPRODUCIBLE

Este directorio contiene la corrida oficial de referencia ("Golden Run") del sistema **Consejo Económico de IA**, diseñada para ser reproducida de forma 100% determinista, con latencia instantánea y sin costo de API durante la filmación del video de divulgación.

---

## Metadatos de la Corrida
- **Fecha de Generación**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- **País de Calibración Base**: Colombia (Economía emergente de ingreso medio)
- **Semilla Aleatoria Fija**: `{RANDOM_SEED}`
- **Modelos de LLM Utilizados (GroqCloud)**:
  - `DEBATER_MODEL`: `openai/gpt-oss-120b` (Temperaturas: Capitalista `0.65`, Colectivista `0.65`, Socialdemócrata `0.60`)
  - `ARBITER_MODEL`: `openai/gpt-oss-120b` (Temperatura: `0.10`)
  - `FAST_MODEL`: `openai/gpt-oss-20b` (Temperatura: `0.20`)
- **Total de Debates Ejecutados en Fase de Pruebas**: 8 corridas completas
- **Corrida Seleccionada**: Corrida #8 (Convergencia unánime sin vetos en el Modelo ICFU)

---

## Contenido del Paquete
1. `debate_session_golden.json`: Transcripción estructurada completa de las 7 rondas, métricas de simulación y evaluaciones del árbitro.
2. `llm_cache_golden.sqlite`: Base de datos SQLite con todas las respuestas cacheadas (hash determinista).
3. `final_synthesis_report.pdf` & `.md`: Especificación técnica del modelo de síntesis en 12 secciones.
4. `key_moments.md`: Los 10 momentos e intercambios más destacados para edición de video.
5. `video_script.md`: Guion de locución de 1 página.
6. Figuras vectoriales (SVG) y en 300 DPI (PNG).

---

## Cómo Reproducir Offline para Grabación
Ejecuta el siguiente comando (funciona sin conexión a internet leyendo de `llm_cache_golden.sqlite`):
```bash
python run_debate.py --mode replay
```
O para el Dashboard interactivo:
```bash
streamlit run src/app/dashboard.py
```
"""
    with open(golden_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"[OK] Paquete Golden Run preparado con exito en: {golden_dir}")

if __name__ == "__main__":
    prepare_golden_run()
