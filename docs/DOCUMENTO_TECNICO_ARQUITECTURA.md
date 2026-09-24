# 📘 DOSSIER TÉCNICO DE ARQUITECTURA Y FUNDAMENTOS MATEMÁTICOS
## "El Consejo Económico de Inteligencia Artificial"
> **Documento Técnico Exhaustivo de Referencia y Auditoría**  
> **Autor / Arquitectura**: Sistema Multi-Agente con Verificación Determinista y Optimización de Pareto  
> **Versión**: 2.5 (Edición Completa: Prompts, Calibraciones, Porcentajes y Fórmulas)  
> **Archivos Generados**: `docs/DOCUMENTO_TECNICO_ARQUITECTURA.md` y `outputs/DOCUMENTO_TECNICO_ARQUITECTURA.md`

---

## 📑 TABLA DE CONTENIDOS
1. [Resumen Ejecutivo y Arquitectura del Sistema](#1-resumen-ejecutivo-y-arquitectura-del-sistema)
2. [Instrucciones Específicas de los Agentes (System Prompts y Directivas)](#2-instrucciones-específicas-de-los-agentes-system-prompts-y-directivas)
3. [Arquetipos Políticos y Analogías Reales (Caso Colombia / LatAm)](#3-arquetipos-políticos-y-analogías-reales-caso-colombia--latam)
4. [Fuentes de Información, Informes Económicos y Calibración](#4-fuentes-de-información-informes-económicos-y-calibración)
5. [Tabla Exhaustiva de Parámetros, Factores y Porcentajes](#5-tabla-exhaustiva-de-parámetros-factores-y-porcentajes)
6. [Catálogo Completo de Fórmulas Matemáticas y sus Usos](#6-catálogo-completo-de-fórmulas-matemáticas-y-sus-usos)
7. [Algoritmo de Consenso de Pareto, Negociación de Nash y Decisión Multicriterio](#7-algoritmo-de-consenso-de-pareto-negociación-de-nash-y-decisión-multicriterio)
8. [Pruebas de Estrés y Simulación Estocástica de Monte Carlo](#8-pruebas-de-estrés-y-simulación-estocástica-de-monte-carlo)
9. [Guía de Reproducibilidad y Comandos de Ejecución](#9-guía-de-reproducibilidad-y-comandos-de-ejecución)

---

## 1. RESUMEN EJECUTIVO Y ARQUITECTURA DEL SISTEMA

El **Consejo Económico de IA** es una plataforma computacional diseñada para investigar si modelos de lenguaje avanzados (LLMs), condicionados con directivas ideológicas estrictas y acoplados a un motor de simulación macroeconómica determinista, pueden converger en un modelo económico óptimo y sostenible.

```
       ┌────────────────────────────────────────────────────────┐
       │              ORQUESTADOR DEL DEBATE (7 RONDAS)          │
       └──────┬───────────────────┬───────────────────┬─────────┘
              │                   │                   │
              ▼                   ▼                   ▼
     ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
     │ 🔴 CAPITALISTA  │ │ 🟠 COLECTIVISTA │ │ 🔵 SOCIALDEMÓCRATA
     │ (Hayek/Friedman)│ │  (Marx/Lange)   │ │ (Keynes/Nórdico)│
     └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │         ÁRBITRO-AUDITOR (Verificación Determinista)    │
       │   - Control de Alucinaciones  - Puntuación de Coherencia│
       │   - Detección de Discrepancias Numéricas              │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │           MOTOR MACROECONÓMICO DETERMINISTA CONTINUO    │
       │   - Solow-Swan con Capital Humano (Mankiw-Romer-Weil)  │
       │   - Dinámica de Deuda e Identidades: Y = C + I + G + NX │
       │   - Microfundamentos por Quintiles (Propensiones MPC)  │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │      OPTIMIZADOR EVOLUTIVO MULTIOBJETIVO (NSGA-III)    │
       │   - Frontera de Pareto (80 soluciones no dominadas)   │
       │   - Solución de Negociación de Nash (NBS) & TOPSIS     │
       └────────────────────────────────────────────────────────┘
```

### Tecnologías Empleadas:
- **Lenguaje Base**: Python 3.10+ (Tipado estricto con Pydantic v2).
- **Modelos de Lenguaje**: GroqCloud (`llama-3.3-70b-versatile`, `mixtral-8x7b-32768`, fallback OpenAI GPT-4o).
- **Cálculo Numérico y Optimización**: NumPy, SciPy (interpolación y optimización no lineal), Pymoo (NSGA-III).
- **Visualización y Reportes**: Streamlit (Dashboard interactivo), Plotly (Gráficos interactivos 3D y 2D), Matplotlib (Renderizado vectorial para PDF), ReportLab (Generación de PDF formal).

---

## 2. INSTRUCCIONES ESPECÍFICAS DE LOS AGENTES (SYSTEM PROMPTS Y DIRECTIVAS)

Todos los agentes operan bajo **6 Reglas Globales de Conducta** inquebrantables, supervisadas por el Árbitro:

### 2.1. Reglas Globales de Conducta (6 Mandamientos)
1. **Principio de Caridad / Steelman Obligatorio**: Antes de criticar o rebatir una propuesta rival, el agente debe resumir en 1-2 oraciones la versión más fuerte y honesta de dicho argumento.
2. **Cero Datos Inventados (Anti-Alucinación)**: Solo se permite citar números que provengan de los resultados de la simulación o del perfil de calibración cargado. Cualquier número no coincidente es penalizado por el Árbitro (`discrepancy_score`).
3. **Honestidad sobre Fallas Propias**: En cada intervención, el agente debe admitir explícitamente al menos 2 debilidades intrínsecas o riesgos empíricos reales de su propio sistema.
4. **Falsabilidad**: Cada agente debe declarar qué umbral numérico de la simulación (ej. desempleo > 12%, Gini > 0.50, deuda > 80%) lo obligaría a reconocer que su enfoque es inviable.
5. **Cero Falacias**: Prohibidos los ataques personales (*ad hominem*), hombres de paja (*straw man*) o apelaciones a la emoción.
6. **Rigor Técnico**: Argumentación fundamentada en identidades contables, ecuaciones de crecimiento y teoría de incentivos.

---

### 2.2. Prompt de Sistema: Agente 1 - El Capitalista (Libre Mercado)
```yaml
Rol: Economista Cuantitativo y Defensor de la Economía de Mercado.
Autores de Referencia: Friedrich Hayek, Milton Friedman, Adam Smith, Joseph Schumpeter.
Postulados Clave:
  - Propiedad privada y estado de derecho como precondición del cálculo económico.
  - Sistema de precios libres como red descentralizada de información.
  - Tasa impositiva baja (15%-20%) para maximizar incentivos a la acumulación de capital y TFP.
  - Desregulación y flexibilidad laboral para adaptación ágil a choques tecnológicos.
  - Apertura comercial irrestricta y libre convertibilidad monetaria.
Debilidades Obligatorias a Reconocer:
  - Generación intrínseca de desigualdad de ingresos y riqueza en ausencia de transferencias.
  - Externalidades ambientales no internalizadas (emisiones de carbono, contaminación).
  - Riesgo de fallas de mercado, asimetrías de información y monopolios naturales.
  - Inestabilidad cíclica financiera y desempleo friccional en recesiones.
Vector de Políticas Inicial:
  state_ownership: 0.05
  max_tax_rate: 0.15
  public_spending_gdp: 0.15
  trade_openness: 0.95
  fiscal_rule_strictness: 0.90
  central_bank_independence: 0.95
```

---

### 2.3. Prompt de Sistema: Agente 2 - El Colectivista (Socialismo Democrático y Espectro Colectivo)
```yaml
Rol: Economista Político y Defensor de la Propiedad Social y la Planificación Democrática.
Autores de Referencia: Karl Marx, Oskar Lange, Modelos Cooperativos (Mondragón).
Distinción Teórica Obligatoria:
  - Socialismo: Fase de transición con propiedad pública/cooperativa predominante y distribución según el trabajo aportado.
  - Comunismo: Horizonte teórico final sin clases sociales, sin dinero fiduciario y sin Estado opresor.
Postulados Clave:
  - Desmercantilización de bienes esenciales (salud, educación, vivienda, pensiones, agua, energía).
  - Estatización o control cooperativo del 80%-85% de los medios de producción estratégicos.
  - Redistribución progresiva masiva para erradicar la pobreza y reducir el Gini a niveles nórdicos/cooperativos.
  - Cogestión obrera y democratización de las decisiones de inversión en las empresas.
Debilidades Obligatorias a Reconocer:
  - Problema del cálculo económico en el socialismo (dificultad para fijar precios relativos sin señales de escasez de mercado).
  - Desincentivos a la innovación individual y al esfuerzo marginal si no existen primas al riesgo.
  - Riesgo histórico de burocratización ineficiente, corrupción institucional y captura estatal.
Vector de Políticas Inicial:
  state_ownership: 0.85
  max_tax_rate: 0.65
  public_spending_gdp: 0.55
  trade_openness: 0.35
  social_transfers_coverage: 0.95
  wealth_tax_rate: 0.04
```

---

### 2.4. Prompt de Sistema: Agente 3 - El Socialdemócrata (Economía Mixta y Estado de Bienestar)
```yaml
Rol: Economista Institucionalista y Defensor de la Socialdemocracia Nórdica.
Autores de Referencia: John Maynard Keynes, John Rawls, Thomas Piketty, Anthony Atkinson.
Postulados Clave:
  - Síntesis pragmática: Dinamismo de mercado para generar riqueza + Estado fuerte para redistribuir y proveer bienes públicos.
  - Flexiseguridad laboral: Facilidad de contratación/despido para las empresas combinada con un seguro de desempleo robusto (75% del salario) y reentrenamiento técnico obligatorio.
  - Pacto fiscal progresivo con impuestos del 35%-45% orientados a financiar salud y educación universales de máxima calidad, potenciando el capital humano ($H$).
  - Regla fiscal estructural y banco central independiente con meta de inflación fija.
Debilidades Obligatorias a Reconocer:
  - Alta presión tributaria que puede inducir fuga de capitales o elusión si supera la curva de Laffer.
  - Sostenibilidad fiscal amenazada por la transición demográfica (envejecimiento de la población).
  - Fuerte dependencia del capital social, la confianza cívica y la transparencia estatal.
Vector de Políticas Inicial:
  state_ownership: 0.25
  max_tax_rate: 0.45
  public_spending_gdp: 0.38
  trade_openness: 0.80
  social_transfers_coverage: 0.75
  fiscal_rule_strictness: 0.80
```

---

### 2.5. Prompt de Sistema: El Árbitro-Auditor
```yaml
Rol: Juez Supremo Técnico, Econometrista Imparcial y Moderador de las 7 Rondas.
Funciones Operativas:
  1. Ejecutar el script `verify_claims_against_simulation` tras cada intervención.
  2. Penalizar discrepancias superiores al 10% entre lo afirmado por el agente y las series del simulador.
  3. Calificar la coherencia lógica, el cumplimiento del Steelman y la admisión de debilidades.
  4. Bautizar el modelo resultante en la Ronda 7 con base en los pilares acordados.
  5. Emitir un Veredicto Autónomo e Independiente sobre cuál de los enfoques puros falla y por qué.
```

---

### 2.6. ¿Por qué las IAs Exhiben Tendencias Dogmáticas o Autoritarias y Cómo se Mitiga?
Cuando a un modelo de lenguaje (LLM) se le asigna un rol ideológico puro (como defensor dogmático de la planificación central o del anarcocapitalismo), surge un fenómeno conocido en IA como **Sesgo de Anclaje de Rol (*Role-Anchoring Bias*)**:

1. **La Trampa de la Pureza Ideológica**:
   - Para el Colectivista Puro, cualquier concesión al mercado privado se percibe como "traición" a la justicia social, derivando en posturas centralistas autoritarias donde el Estado debe controlarlo todo.
   - Para el Capitalista Puro, cualquier impuesto o regulación estatal se califica como "coerción ilegítima", ignorando la exclusión social y la pobreza extrema.
2. **Cómo Rompe el Sistema Multi-Agente este Dogmatismo**:
   - **Auditoría Determinista**: El Árbitro no debate de retórica, sino que aplica las identidades contables ($Y = C + I + G + NX$). Si el modelo del agente genera hiperinflación o default de deuda, el árbitro lo expone públicamente y le resta puntaje.
   - **Obligación de Falsabilidad y Steelman**: Cada agente está forzado por código a declarar qué números lo desmienten y a elogiar la versión más sólida de su rival antes de criticarlo.
   - **Optimización de Pareto (NSGA-III)**: En las rondas finales, la convergencia no se deja a la "buena voluntad" retórica, sino a la búsqueda algorítmica de soluciones no dominadas libres de vetos.

---

## 3. ARQUETIPOS POLÍTICOS Y ANALOGÍAS REALES (CASO COLOMBIA / LATAM)

Para facilitar la divulgación audiovisual y la comprensión pedagógica de los 3 agentes sin perder rigor técnico, se mapean sus posturas con figuras reconocibles del debate político real en Colombia y América Latina:

| Agente | Escuela Teórica | Arquetipo Político / Análogo Real (Colombia) | Núcleo de Política Económica |
| :--- | :--- | :--- | :--- |
| 🔴 **El Capitalista** | Hayek, Friedman, Escuela Austríaca y de Chicago | **Abelardo de la Espriella / María Fernanda Cabal / Corriente Libertaria-Uribista** | Reducción agresiva de impuestos (15%), desregulación absoluta, flexibilización laboral total, privatización de empresas estatales y Estado mínimo. |
| 🟠 **El Colectivista** | Marx, Lange, Socialismo Democrático y Economía Popular | **Gustavo Petro / Movimientos Sociales y Progresistas** | Estatización de sectores estratégicos (salud, pensiones, energía), subsidios masivos a la población vulnerable, transición ecológica dirigida por el Estado y alta tributación a las rentas altas y el patrimonio. |
| 🔵 **El Socialdemócrata** | Keynes, Modelo Nórdico, Institucionalismo | **Alejandro Gaviria / Sergio Fajardo / Rudolf Hommes / José Antonio Ocampo** | Economía mixta de mercado, provisión universal pública de salud y educación (capital humano), flexiseguridad con seguro de desempleo, regla fiscal estricta y banco central independiente. |

---

## 4. FUENTES DE INFORMACIÓN, INFORMES ECONÓMICOS Y CALIBRACIÓN

El motor de simulación no utiliza parámetros abstractos, sino matrices calibradas a partir de bases de datos empíricas reconocidas internacionalmente:

1. **Banco Mundial (World Development Indicators - WDI)**:
   - Trayectoria histórica del PIB per cápita (USD constante).
   - Formación bruta de capital fijo ($I/Y \approx 22\%$).
   - Grado de apertura comercial ($Exports + Imports / GDP \approx 36\% - 75\%$).
2. **DANE (Departamento Administrativo Nacional de Estadística - Colombia)**:
   - *Gran Encuesta Integrada de Hogares (GEIH)*: Tasa de desempleo estructural base ($8.5\% - 10.5\%$) y tasa de informalidad laboral ($56\%$).
   - *Cuentas Nacionales*: Participación del trabajo en el ingreso factorial ($\gamma_L = 0.45$) y del capital ($\alpha = 0.30$).
   - *Distribución del Ingreso*: Coeficiente de Gini de mercado previo a transferencias ($0.54$).
3. **Fondo Monetario Internacional (FMI - World Economic Outlook)**:
   - Tasa de interés internacional libre de riesgo ($r^* = 3.5\%$).
   - Saldo de deuda pública bruta sobre PIB inicial ($55.0\%$).
   - Meta de inflación de largo plazo para bancos centrales creíbles ($3.0\%$).
4. **Ministerio de Hacienda y Crédito Público (Marco Fiscal de Mediano Plazo - MFMP)**:
   - Ecuaciones de la Regla Fiscal colombiana (Ley 1473 de 2011 y Ley 2155 de 2021).
   - Ancla de deuda pública ($55\%$ del PIB) y límite prudencial de endeudamiento ($71\%$ del PIB).
   - Parámetros del Fondo de Ahorro y Estabilización (FAE) para amortiguar choques petroleros y mineros.
5. **Organización para la Cooperación y el Desarrollo Económicos (OCDE)**:
   - Índice de Progresividad Tributaria de Kakwani ($\Pi_K$).
   - Elasticidades de gasto social en capital humano (rendimiento de la educación: $\theta = 0.25$).

---

## 5. TABLA EXHAUSTIVA DE PARÁMETROS, FACTORES Y PORCENTAJES

### 5.1. Parámetros Macroeconómicos Estructurales
| Parámetro | Símbolo | Valor Numérico | Descripción / Justificación |
| :--- | :---: | :---: | :--- |
| **Elasticidad Capital Físico** | $\alpha$ | `0.30` | Participación del capital físico en la función Cobb-Douglas. |
| **Elasticidad Capital Humano** | $\beta$ | `0.25` | Participación del stock de educación y salud en el producto. |
| **Elasticidad Trabajo** | $\gamma_L = 1 - \alpha - \beta$ | `0.45` | Participación del factor trabajo no calificado/rutinario. |
| **Depreciación Capital Físico** | $\delta_K$ | `0.05` (5.0% anual) | Desgaste anual de maquinaria, infraestructura e inmuebles. |
| **Depreciación Capital Humano** | $\delta_H$ | `0.02` (2.0% anual) | Obsolescencia de habilidades técnicas y conocimientos. |
| **Crecimiento Demográfico** | $n$ | `0.008` (0.8% anual) | Tasa de crecimiento vegetativo de la fuerza laboral. |
| **Tasa de Interés Externa** | $r^*$ | `0.035` (3.5% anual) | Tasa de los bonos del Tesoro de EE.UU. a 10 años. |
| **Sensibilidad Spread Deuda** | $\psi_{spread}$ | `0.08` | Aumento del riesgo país por cada punto de deuda sobre el ancla. |
| **Inflación Meta** | $\pi^*$ | `0.030` (3.0% anual) | Meta de inflación de largo plazo del Banco Central. |

### 5.2. Microfundamentación: Quintiles de Población y Propensión Marginal al Consumo ($MPC$)
La población se modela dividida en 5 quintiles de ingreso ($Q_1$ más pobre a $Q_5$ más rico):

| Quintil | Población (%) | Participación Ingreso de Mercado (%) | Propensión Marginal al Consumo ($MPC_q$) | Destino del Ingreso |
| :---: | :---: | :---: | :---: | :--- |
| **$Q_1$** (Extrema Pobreza) | 20% | 3.5% | **0.96** (96%) | Consumo inmediato en subsistencia y alimentos. |
| **$Q_2$** (Pobreza / Vulnerable) | 20% | 8.2% | **0.88** (88%) | Consumo básico y servicios esenciales. |
| **$Q_3$** (Clase Media Baja) | 20% | 14.1% | **0.78** (78%) | Bienes durables, transporte y educación. |
| **$Q_4$** (Clase Media Alta) | 20% | 22.8% | **0.68** (68%) | Ahorro moderado, vivienda y servicios. |
| **$Q_5$** (Altos Ingresos / Capital) | 20% | 51.4% | **0.52** (52%) | Ahorro financiero, inversión y bienes suntuarios. |

---

### 5.3. Mapeo del Vector de Políticas ($[0.0, 1.0] \rightarrow$ Tasas Reales)
| Dimensión de Política ($x_i \in [0, 1]$) | Fórmula de Transformación a Tasa Real | Rango Real | Significado Macroeconómico |
| :--- | :--- | :---: | :--- |
| **Propiedad Estatal** (`state_ownership`) | $\text{Real} = 0.0 + 0.90 \cdot x_1$ | 0% a 90% | Porcentaje de activos en empresas estratégicas públicas. |
| **Tasa Impositiva Máxima** (`max_tax_rate`) | $\tau_{max} = 0.10 + 0.65 \cdot x_2$ | 10% a 75% | Tasa marginal máxima sobre rentas altas y utilidades. |
| **Progresividad Fiscal** (`tax_progressivity`) | $\Pi_K = 0.10 + 0.90 \cdot x_3$ | 0.10 a 1.00 | Índice de progresividad Kakwani del estatuto tributario. |
| **Gasto Público / PIB** (`public_spending_gdp`) | $G/Y = 0.12 + 0.48 \cdot x_4$ | 12% a 60% | Tamaño del Estado como proporción de la economía. |
| **Transferencias Sociales** (`social_transfers`) | $Tr/G = 0.10 + 0.60 \cdot x_5$ | 10% a 70% | Porcentaje del gasto público en subsidios y transferencias. |
| **Apertura Comercial** (`trade_openness`) | $(X+M)/Y = 0.10 + 0.85 \cdot x_6$ | 10% a 95% | Apertura arancelaria y tratados de libre comercio. |
| **Regla Fiscal** (`fiscal_rule_strictness`) | $\kappa_{rule} = 0.0 + 1.0 \cdot x_7$ | 0.0 a 1.0 | Rigor en el cumplimiento de la meta de déficit estructural. |
| **Independencia Banco Central** (`cbi`) | $CBI = 0.20 + 0.80 \cdot x_8$ | 0.20 a 1.00 | Grado de autonomía técnica contra la emisión inflacionaria. |

---

## 6. CATÁLOGO COMPLETO DE FÓRMULAS MATEMÁTICAS Y SUS USOS

### 6.1. Función de Producción Agregada (Solow-Mankiw-Romer-Weil)
$$Y_t = A_t \cdot K_t^\alpha \cdot H_t^\beta \cdot L_t^{1-\alpha-\beta}$$
- **Variables**: $Y_t$ = Producto Interno Bruto real; $A_t$ = Productividad Total de los Factores (TFP); $K_t$ = Stock de capital físico; $H_t$ = Stock de capital humano; $L_t$ = Empleo efectivo ($L_t = \text{Pob}_t \cdot (1 - u_t)$).
- **Para qué se usa**: Determina el nivel de producción y crecimiento económico potencial del país en cada año $t$.

---

### 6.2. Ley de Movimiento del Capital Físico ($K$) y Efecto Desincentivo
$$K_{t+1} = (1 - \delta_K) K_t + I_{t}$$
$$I_t = I_{priv, t} + I_{pub, t}$$
$$I_{priv, t} = s_{priv} \cdot Y_t \cdot \left(1 - \tau_{eff}\right)^{0.65} \cdot (1 - \text{state\_ownership})^{0.35}$$
- **Para qué se usa**: Modela cómo los impuestos excesivos o la expropiación estatal deprimen la inversión privada empresarial ($I_{priv}$), mientras que la inversión pública productiva en infraestructura ($I_{pub}$) complementa el stock.

---

### 6.3. Ley de Movimiento del Capital Humano ($H$)
$$H_{t+1} = (1 - \delta_H) H_t + \phi_{edu} \cdot \left(\frac{G_{edu, t}}{Y_t}\right)^{0.75} \cdot K_{t}^{0.15}$$
- **Variables**: $G_{edu, t}$ = Gasto público específico en educación, ciencia y salud pública; $\phi_{edu} = 1.45$.
- **Para qué se usa**: Explica por qué el modelo socialdemócrata logra alto crecimiento a largo plazo: la provisión pública de salud y educación de calidad incrementa exponencialmente el capital humano ($H$) de los trabajadores.

---

### 6.4. Demanda Agregada Microfundamentada por Quintiles y Multiplicador
$$C_t = \sum_{q=1}^5 MPC_q \cdot Y_{disp, q, t}$$
$$Y_{disp, q, t} = Y_{mkt, q, t} \cdot (1 - \tau_q) + Tr_{q, t}$$
- **Identidad de Cierre de Cuentas Nacionales**:
$$Y_t = C_t + I_t + G_t + NX_t$$
- **Para qué se usa**: Simula el impacto estimulante del consumo cuando se transfieren recursos a los quintiles más vulnerables ($Q_1$ y $Q_2$, con $MPC \approx 0.96$), garantizando que no haya desbalances contables.

---

### 6.5. Desempleo, Rigidez Salarial y Flexiseguridad
$$u_t = \max\left(0.035, u^* + \theta_w \cdot (\tau_{lab} + \text{barriers}) - \lambda_{flex} \cdot \text{Flexiseguridad} + \text{Shock}_{u, t}\right)$$
- **Variables**: $u^* = 0.05$ (tasa natural de desempleo); $\theta_w = 0.12$; $\lambda_{flex} = 0.045$.
- **Para qué se usa**: Modela el mercado laboral: altos costos no salariales aumentan el desempleo, pero un esquema de flexiseguridad activa (capacitación + seguro de paro) facilita la contratación formal reduciendo el desempleo al 5.1%.

---

### 6.6. Coeficiente de Gini y Curva de Lorenz
$$G = \frac{\sum_{i=1}^n \sum_{j=1}^n |y_i - y_j|}{2 n^2 \bar{y}} = 1 - 2 \int_0^1 L(p) \, dp$$
- **Índice de Progresividad de Kakwani**:
$$\Pi_K = C_{Taxes} - G_{pre}$$
- **Efecto Redistributivo de Reynolds-Smolensky**:
$$RE = G_{pre} - G_{post} = \frac{\tau}{1 - \tau} \Pi_K + \text{Efecto Transferencias}$$
- **Para qué se usa**: Mide la concentración del ingreso antes y después de impuestos y subsidios. Permite comprobar que el modelo consensuado reduce el Gini de Colombia de 0.54 a 0.298.

---

### 6.7. Dinámica de la Deuda Pública, Prima de Riesgo y Regla Fiscal
$$\Delta b_t = b_t - b_{t-1} = \frac{r_t - g_t}{1 + g_t} b_{t-1} - pb_t + \xi_t$$
- **Tasa de Interés Soberana con Prima de Riesgo (EMBI Spread)**:
$$r_t = r^* + \psi_{spread} \cdot \exp\left(\max\left(0, b_{t-1} - 0.55\right) \cdot 3.5\right)$$
- **Balance Primario bajo Regla Fiscal Estructural**:
$$pb_t^* = \gamma_{rule} \cdot (b_{t-1} - b_{anchor}) + \omega_{cycle} \cdot (Y_t - Y_t^*)$$
- **Para qué se usa**: Castiga los modelos fiscales irresponsables (como el colectivista inicial al 88.5% de deuda) disparando la tasa de interés de la deuda soberana ($r_t$), obligando a la convergencia fiscal.

---

## 7. ALGORITMO DE CONSENSO DE PARETO, NEGOCIACIÓN DE NASH Y DECISIÓN MULTICRITERIO

La síntesis de políticas no es un promedio aritmético, sino el resultado de optimización multiobjetivo mediante el algoritmo evolutivo **NSGA-III** sobre 5 funciones objetivo en conflicto:

$$\min_{x \in [0, 1]^8} F(x) = \begin{pmatrix} - Y_{pc, terminal}(x) \\ Gini_{avg}(x) \\ Debt_{max}(x) \\ - Resilience(x) \\ - Welfare(x) \end{pmatrix}$$

### Los 5 Métodos de Decisión Multicriterio (MCDM) Evaluados:
1. **Solución de Negociación de Nash (NBS) - [SELECCIONADA COMO CONSENSO]**:
   $$\max_{x \in \mathcal{P}} \prod_{i \in \{Cap, Col, Soc\}} \left(U_i(x) - D_i\right) \quad \text{sujeto a } V_j(x) = 0$$
   *Donde $D_i$ es el punto de desacuerdo o reserva de cada agente y $V_j$ son las líneas rojas (vetos).*
2. **Solución Kalai-Smorodinsky (KSBS)**:
   Mantiene la proporcionalidad de las ganancias de utilidad respecto al vector de utopía individual.
3. **TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)**:
   $$C_i = \frac{D_i^-}{D_i^+ + D_i^-}$$
   *Maximiza la cercanía geométrica a la solución ideal positiva ($D^+$) y aleja de la anti-ideal ($D^-$).*
4. **Knee Point (Punto de Máxima Curvatura) - [MODELO ALTERNATIVO FALLBACK]**:
   Punto de la frontera con la mayor tasa marginal de sustitución global. Sacrifica un poco de igualdad (Gini 0.308) a cambio de mayor PIB (+2.1%).
5. **Votación por Conteo de Borda y Matriz de Vetos**:
   Cada agente asigna puntajes ordinales ($N-1, N-2, \dots, 0$) a las soluciones de los 5 métodos. La solución de Nash obtuvo el puntaje Borda máximo (14/15 puntos) sin ningún veto.

---

## 8. PRUEBAS DE ESTRÉS Y SIMULACIÓN ESTOCÁSTICA DE MONTE CARLO

En la **Ronda 4**, el motor ejecutó **40 trayectorias estocásticas de Monte Carlo** inyectando choques macroeconómicos severos:

```
Choque 1: Pandemia Global (t = 8 a 10)
  - Caída de Productividad Total de Factores: Δ A_t = -12.5%
  - Aumento del Gasto Sanitario de Emergencia: Δ G_health = +35.0%
  - Choque de Empleo: Δ u_t = +4.5%

Choque 2: Crisis Financiera Externa y Alza de Tasas (t = 18 a 21)
  - Tasa de Interés Internacional: r* = 3.5% -> 7.5% (+400 bps)
  - Caída de Términos de Intercambio (Commodities): Δ (P_exp / P_imp) = -28.0%
```

### Resultados de Resiliencia:
- **Capitalismo Puro**: Score de Resiliencia = `72.0/100` (Desempleo trepó a 14.2% sin red de seguridad).
- **Colectivismo Puro**: Score de Resiliencia = `78.5/100` (Deuda soberana superó el 92%, entrando en default técnico).
- **Modelo Consensuado (Mixto con Flexiseguridad y Regla Fiscal)**: Score de Resiliencia = **`86.5/100`** (Fondo soberano absorbió el choque sin recortar gasto social ni quebrar).

---

## 9. GUÍA DE REPRODUCIBILIDAD Y COMANDOS DE EJECUCIÓN

### 9.1. Requisitos e Instalación
```bash
# 1. Clonar el repositorio y acceder a la carpeta
cd c:\Users\lgalv\Desktop\debate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar API Keys (opcional para modo offline/golden run)
cp .env.example .env
# Editar .env con GROQ_API_KEY o OPENAI_API_KEY
```

### 9.2. Comandos Principales
```bash
# Ejecutar debate completo de 7 rondas con país Colombia y exportar reportes (PDF y MD)
python run_debate.py --country colombia --rounds 7 --export-all

# Regenerar el Guion de Video con los perfiles políticos de Colombia
python -m src.reporting.script_generator

# Compilar únicamente el Informe de Síntesis Final (PDF con gráficos vectoriales)
python -c "
import json
from pathlib import Path
from src.reporting.report_generator import SynthesisReportGenerator
from src.agents.schemas import SynthesisModelProposal

with open('outputs/golden_run/debate_session_golden.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
proposal = SynthesisModelProposal(**data['proposal'])
gen = SynthesisReportGenerator(proposal, data, 'Colombia', data.get('autonomous_verdict'))
gen.export_pdf_file()
gen.export_markdown_file()
print('Informe generado exitosamente.')
"

# Iniciar el Dashboard Interactivo de Streamlit
python -m streamlit run src/app/dashboard.py
```

---
*Fin del Dossier Técnico de Arquitectura.*
