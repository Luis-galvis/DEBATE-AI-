# GOLDEN RUN — PAQUETE MAESTRO DE GRABACIÓN REPRODUCIBLE

Este directorio contiene la corrida oficial de referencia ("Golden Run") del sistema **Consejo Económico de IA**, diseñada para ser reproducida de forma 100% determinista, con latencia instantánea y sin costo de API durante la filmación del video de divulgación.

---

## Metadatos de la Corrida
- **Fecha de Generación**: 21/09/2026 15:36:07
- **País de Calibración Base**: Colombia (Economía emergente de ingreso medio)
- **Semilla Aleatoria Fija**: `42`
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
