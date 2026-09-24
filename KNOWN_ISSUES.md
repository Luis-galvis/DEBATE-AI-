# Registro de Limitaciones y Problemas Conocidos (KNOWN_ISSUES.md)

Este documento enumera formalmente las limitaciones metodológicas, técnicas y de modelado identificadas durante la auditoría integral del sistema "Consejo Económico de IA", ordenadas por nivel de severidad.

---

## 1. Severidad Media-Alta: Sesgo de Modelo Base Compartido (LLM Homogeneity)
- **Descripción**: Los tres agentes debatientes y el Árbitro utilizan como backend el mismo modelo (`openai/gpt-oss-120b`). A pesar de perfiles de temperatura diferenciados (0.7 vs 0.3) y exhaustivos *system prompts* de escuela económica, comparten el mismo espacio latente pre-entrenado.
- **Impacto**: Riesgo de convergencia estilística o acuerdos no fundamentados si no se fuerzan penalizaciones numéricas.
- **Mitigación Implementada**: Obligatoriedad de citar claims matemáticos verificados por código (`ArbitrationReferee`), penalización de 2.0 puntos por falsedad empírica, cálculo formal de compromiso mediante NSGA-III (TOPSIS/Nash/Kalai-Smorodinsky) independiente del consenso retórico.

---

## 2. Severidad Media: Discrepancia en Calibración Estilizada para Países Emergentes
- **Descripción**: La simulación base utiliza funciones de agregación Solow-Swan y curvas de Phillips estandarizadas. Al contrastar con datos reales de Colombia, se observa una discrepancia en el Gini inicial pre-reforma (0.354 simulado vs 0.525 real, error ~32.6%) debido a que el modelo base no captura la extrema concentración histórica de tierras e informalidad estructural previa a las políticas.
- **Impacto**: Las trayectorias de reducción de desigualdad en el modelo miden el impacto relativo de las políticas sobre una base normalizada, no el nivel absoluto microeconométrico exacto del DANE.
- **Mitigación Implementada**: Documentación explícita de la tabla de calibración en `AUDIT_REPORT.md` y advertencia en `ASSUMPTIONS.md`.

---

## 3. Severidad Baja: Rendimiento Computacional de la Capa Micro ABM (Mesa)
- **Descripción**: La simulación de 1,000 agentes heterogéneos con redes de intercambio en Mesa toma ~1.4 segundos por corrida completa, lo cual hace inviable su inclusión dentro del bucle interno de optimización genética de NSGA-III (que realiza 300 evaluaciones en ~240 ms).
- **Impacto**: NSGA-III optimiza sobre el motor macro continuo vectorizado (`SolowSwanEngine`), mientras que la capa ABM se ejecuta exclusivamente como paso de validación microeconómica post-optimización.
- **Mitigación Implementada**: Capa ABM desacoplada detrás del flag `--enable-abm` en `src/simulation/abm_micro.py`.

---

## 4. Severidad Baja: Agregación Macroeconómica Discreta Anual
- **Descripción**: El motor computa el equilibrio de mercado y la acumulación de factores en pasos de tiempo anuales ($\Delta t = 1$ año) durante un horizonte de 30 periodos.
- **Impacto**: No se capturan dinámicas de liquidez intradiarias, pánicos cambiarios semanales ni subastas de bonos de alta frecuencia.
- **Mitigación Implementada**: Modelado de choques de estrés discretos (`shocks.py`) con factores de amplificación no lineal y primas de riesgo soberanas endógenas.
