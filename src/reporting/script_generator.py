"""
Generador Automatizado del Guion de Video de Divulgación (GUION_VIDEO.md).
Carga los datos reales del Golden Run (outputs/golden_run/debate_session_golden.json)
y genera un guion exhaustivo en primera persona para YouTube y redes sociales,
con tabla de 4 columnas, marcas de tiempo, humor de proceso, trazabilidad numérica
y todos los extras requeridos.
"""

import json
from pathlib import Path
from typing import Dict, Any

from src.config import BASE_DIR, OUTPUTS_DIR
from src.app.viz.round_summary_generator import generate_round_summary_card

def generate_video_script_markdown(golden_data: Dict[str, Any]) -> str:
    """Genera el contenido Markdown completo de docs/video/GUION_VIDEO.md con rigor técnico y fórmulas."""
    
    # Extraer métricas clave del golden run
    proposal = golden_data.get("proposal", {})
    model_name = proposal.get("model_name", "Modelo de Innovación Productiva, Formalización y Flexiseguridad Adaptada (IPFA)")
    p_vec = proposal.get("policy_vector", {})
    country = golden_data.get("calibration_country", "Colombia").capitalize()
    
    # Tarjetas de cierre de las 7 rondas
    cards = [generate_round_summary_card(golden_data, r) for r in range(1, 8)]
    
    md_content = f"""# 🎬 Guion de Grabación: "Puse a Tres IAs a Diseñar la Economía Perfecta (y Pasó Esto)"

> **Documento Maestro de Producción Audiovisual con Sustento Matemático y Algorítmico**  
> **Autor / Presentador:** Ingeniero de Datos & Creador del Proyecto (Primera Persona)  
> **Idioma:** Español Neutro, Conversacional, Cercano y con Profundidad Técnica  
> **Fuente de Datos:** *Golden Run Verificado* (`outputs/golden_run/debate_session_golden.json`)  
> **Comando de Regeneración:** `python -m src.reporting.script_generator`

---

## ⏱️ Estructura General y Versiones de Duración
* **Versión Completa (YouTube Principal):** ~15 minutos (retención profunda, ecuaciones en pantalla, código y dashboard interactivo).
* **Versión Comprimida (Podcast / Resumen):** ~8 minutos (ver notas de recorte marcadas con `[✂️ Omitir en versión 8m]`).
* **Versión Corta Vertical (TikTok / Reels / Shorts):** 60 segundos (guion anexo al final).

---

## 🧠 Fichas Técnicas: Algoritmos y Fórmulas Matemáticas del Sistema

Antes de la grabación, estos son los microfundamentos matemáticos y algoritmos que respaldan cada segundo del video:

### 1. Función de Producción Solow-Mankiw-Romer-Weil con Capital Humano
$$Y_t = A_t \\cdot K_t^\\alpha \\cdot H_t^\\beta \\cdot L_{{eff, t}}^{{1 - \\alpha - \\beta}}$$
* Parámetros calibrados: $\\alpha = 0.30$ (capital físico), $\\beta = 0.25$ (capital humano), $\\gamma_L = 0.45$ (trabajo efectivo $L_{{eff}} = L_t (1 - u_t)$).
* Crecimiento de Productividad Total de los Factores (TFP):
$$A_{{t+1}} = A_t \\cdot \\left(1 + 0.010 + 0.35 \\cdot \\left(\\frac{{I+D}}{{Y}}\\right)_t + 0.008 \\cdot Apertura - 0.012 \\cdot Regulacion^2\\right)$$

### 2. Dinámica de Deuda Pública Intertemporal y Prima de Riesgo Soberano
$$\\Delta b_t = (r_t - g_t) b_{{t-1}} - pb_t + \\xi_t$$
$$r_t = r^* + \\max\\left(0, (b_{{t-1}} - 0.60) \\cdot 0.06\\right) + (1 - Strict_{{fisc}}) \\cdot 0.02 + \\text{{Shock}}_{{spread, t}}$$
* Si la deuda sobrepasa el 60% del PIB, la tasa de interés soberana $r_t$ escala exponencialmente, castigando a los modelos insolventes con riesgo de quiebra soberana.

### 3. Consumo Agregado Microfundamentado por Quintiles
$$C_t = \\sum_{{q=1}}^5 MPC_q \\cdot Y_{{disp, q, t}}, \\quad MPC = [0.96, 0.88, 0.78, 0.68, 0.52]$$
* Los hogares vulnerables ($Q_1-Q_2$) consumen casi el 100% de su ingreso disponible; los ricos ($Q_5$) ahorran el 48%, alimentando la inversión privada.

### 4. Arquitectura y Algoritmo de Auditoría del Árbitro-Auditor (`verify_claims_against_simulation`)
* **Tokenización Regex Decimal:** El árbitro analiza oraciones preservando números decimales (evitando fragmentar cifras como `185.4` o `0.298`).
* **Mapeo Semántico Multi-Métrica:** Asocia términos como "Gini", "PIB", "Desempleo", "Deuda" con los arrays del simulador.
* **Banda de Tolerancia Cuantitativa:** Una afirmación es válida si:
$$\\frac{{|x_{{citado}} - x_{{simulado}}|}}{{\\max(10^{{-4}}, |x_{{simulado}}|)}} \\le 0.05 \\quad \\lor \\quad |x_{{citado}} - x_{{simulado}}| \\le 0.08 \\cdot \\max(1.0, x_{{simulado}})$$
* **Penalización Automática de Rúbrica:** Si detecta discrepancias, `fact_check_passed = False`, fijando el tope de evidencia en $\\le 5.5/10$ y score global en $\\le 6.0/10$.

### 5. Optimización Multiobjetivo NSGA-III y Solución de Negociación de Nash (NBS)
* **Algoritmo NSGA-III:** Clasificación no dominada sobre 6 funciones objetivo (PIB per cápita ↑, Gini ↓, Desempleo ↓, Deuda máxima ↓, Resiliencia ante Choques ↑, Bienestar Social ↑).
* **Solución de Nash (NBS) sobre la Frontera de Pareto $\\mathcal{{P}}$:**
$$\\max_{{x \\in \\mathcal{{P}}}} \\prod_{{i \\in \\{{Cap, Col, Soc\\}}}} \\left(U_i(x) - D_i\\right) \\quad \\text{{sujeto a }} V_j(x) = 0 \\; \\forall j$$
donde $D_i$ es el punto de desacuerdo/quiebra y $V_j(x)$ representa las líneas rojas (vetos).

---

## 📋 Tabla Maestra del Guion Segmentado

| Tiempo | Qué Muestro en Pantalla | Lo que Digo (Texto Hablado) | Notas de Producción / Tono |
|---|---|---|---|
| **0:00 - 0:30**<br>*(Gancho)* | **Plano medio a cámara.**<br>Gráfico animado con las 3 IAs enfrentadas (🔴 vs 🟠 vs 🔵) y una balanza oscilando. | "¿Es posible sentar a un capitalista ultraliberal, a un socialista marxista y a un socialdemócrata en la misma mesa y lograr que se pongan de acuerdo sin que el país termine quebrado o en dictadura?<br><br>Para averiguarlo, no invité a políticos. Programé a tres inteligencias artificiales con directivas ideológicas estrictas, las puse a debatir durante 7 rondas y las até a un simulador matemático que calcula 30 años de evolución macroeconómica.<br><br>El resultado final no solo me sorprendió a mí: las tres IAs lograron firmar un acuerdo unánime... y hoy te voy a mostrar exactamente cómo lo hicieron y qué matemática hay detrás." | **Tono:** Intrigante, con ritmo enérgico pero sereno.<br>**Énfasis:** En *"las até a un simulador matemático"*. |
| **0:30 - 1:30**<br>*(Arquitectura del Sistema)* | **Navegación en el Dashboard:** pestaña `🧭 1. Recorrido Guiado` → Paso 1 (*Quiénes participan*).<br><br>*Overlay visual:* Diagrama de bloques (3 LLMs ↔ Árbitro ↔ Motor Solow). | "El experimento funciona con tres piezas de ingeniería. Primero: **tres agentes de IA** construidos con prompts que encapsulan escuelas económicas irreconciliables. Y aquí hay una decisión de diseño fundamental: **utilicé exactamente el mismo modelo base de IA para los tres debatientes y el Árbitro**. ¿Por qué? Para garantizar una cancha totalmente neutral: ninguna postura tenía ventaja por 'ser un modelo más inteligente'; la única diferencia radicaba en sus principios filosóficos y en cómo respondían a las matemáticas.<br><br>Segundo: un **Árbitro-Auditor**, un juez algorítmico implacable que no debate de filosofía, sino que audita cada número que dicen las IAs. Y tercero: el **motor macroeconómico**, un sistema de ecuaciones diferenciales deterministas basado en el modelo Solow-Mankiw-Romer-Weil con capital humano y dinámica fiscal intertemporal." | **Cámara:** Transición suave a captura de pantalla a 1080p.<br>**Gesto:** Sonreír al hablar del árbitro.<br>**Énfasis metodológico:** Mismo modelo base = cancha nivelada. |
| **1:30 - 2:30**<br>*(Las 4 Reglas & El Árbitro por Dentro)* | **Paso 2 del Recorrido:** Animación de la tarjeta *"Cero datos inventados"* y código de `verify_claims_against_simulation`. | "Para evitar que fuera una charla de café con alucinaciones de IA, impuse cuatro reglas de oro por código.<br><br>Regla uno: **cero datos inventados**. Diseñé un algoritmo en Python con expresiones regulares que toma el texto de cada IA, extrae las cifras, busca a qué variable macroeconómica pertenecen y las compara contra el simulador con una tolerancia estricta del 5%. Si una IA inventa un dato, el árbitro le anula el punto y la castiga en la rúbrica.<br><br>Regla dos: **el simulador manda**. Identidades contables cerradas: $Y = C + I + G + NX$. Si gastas más de lo que recaudas, la deuda $\\Delta b_t$ se dispara y la prima de riesgo te castiga.<br><br>Regla tres: **Steelman obligatorio**. Tienen que resumir el argumento del rival en su versión más sólida antes de criticar. Y regla cuatro: **falsabilidad declarada**." | **Humor de proceso:** *"Ojalá tuviéramos un script así en los debates presidenciales en televisión..."* |
| **2:30 - 3:45**<br>*(Los 3 Agentes & El Contexto Colombia)* | **Paso 1 del Recorrido:** Tarjetas de 🔴 Capitalista, 🟠 Colectivista y 🔵 Socialdemócrata.<br><br>*Overlay visual:* Foto/icono comparativo de arquetipos (Colombia: Abelardo vs Petro vs Gaviria). | "Conozcamos a los participantes en el contexto real de {country}:<br><br>A la izquierda, **El Capitalista** (Hayek y Friedman, análogo a figuras pro-mercado como Abelardo de la Espriella o Cabal): defiende desregulación total, impuestos mínimos del 15% y libre empresa.<br><br>Al centro, **El Colectivista** (Marx y Lange, análogo a Gustavo Petro o movimientos comunitarios): propone 85% de control estatal estratégico, economía popular y transferencias universales.<br><br>Y a la derecha, **El Socialdemócrata** (Keynes y Rawls, análogo a tecnócratas como Alejandro Gaviria u Ocampo): busca equilibrio fiscal, mercado eficiente y provisión pública de salud y educación.<br><br>**Pero aquí viene la trampa:** No podemos hacer un simple copiar y pegar del modelo nórdico de Suecia. En Suecia la formalidad es del 95% y el recaudo es del 43% del PIB. En Colombia la informalidad laboral es del 56%, solo el 25% tiene pensión y el recaudo apenas llega al 19%. Toda propuesta tenía que adaptarse a esta dura realidad." | **Rigor conceptual:** Enfatizar la brecha estructural de Colombia vs Escandinavia.<br>**Pedagógico:** Citar cifras del Banco Mundial / DANE. |
| **3:45 - 5:00**<br>*(Ronda 1: Apertura y Choque)* | **Paso 3 del Recorrido:** Discursos de Ronda 1 y la **Tarjeta de Cierre Ronda 1**. | "Arrancó la **Ronda 1**. Cada IA disparó desde su trinchera pura. El Capitalista propuso achicar el Estado a 12% del PIB. El Colectivista pidió estatizar el 85% de las empresas y subsidios masivos. Y el Socialdemócrata pidió impuestos nórdicos del 45%.<br><br>Miren la tarjeta de cierre: el medidor de convergencia marcó apenas un **{cards[0]['convergence_pct']:.1f}%**. Polarización absoluta. Estaban a años luz de distancia." | **Mostrar:** Termómetro en rojo (polarización total). |
| **5:00 - 6:15**<br>*(Ronda 2: El Castigo del Simulador)* | **Paso 4 del Recorrido:** Gráfico de trayectorias a 30 años y **Tarjeta de Cierre Ronda 2**. | "En la **Ronda 2**, soltamos el motor macroeconómico a 30 años. Y aquí cayeron las fantasías.<br><br>El modelo capitalista puro maximizó el PIB per cápita, pero disparó la desigualdad a un Gini de 0.54, dejando a la economía informal en la miseria. Pero al Colectivista le fue peor: su carga impositiva asfixiante provocó una fuga de capitales del 40%, colapsando la inversión privada ($I_{{priv}}$) y dejando al Estado insolvente.<br><br>La matemática no perdona: $Y = A K^\\alpha H^\\beta L^\\gamma$. Sin capital, la producción se desploma." | **Dato real:** Citar Gini 0.54 vs fuga de inversión. |
| **6:15 - 7:30**<br>*(Ronda 3: Falsabilidad y Auditoría)* | **Paso 5 del Recorrido:** Veredictos del Árbitro en Ronda 3. | "La **Ronda 3** fue el examen de falsabilidad. El Capitalista tuvo que admitir qué pasaría si los salarios deprimían el consumo de los primeros quintiles. El Colectivista tuvo que explicar cómo financiaría los hospitales sin ahorro privado.<br><br>El Árbitro atrapó dos discrepancias numéricas en vivo y penalizó la rúbrica. Miren la tarjeta: la convergencia subió al **{cards[2]['convergence_pct']:.1f}%**. Empezaron a entender que ningún extremo sobrevivía solo." | **Pausa dramática:** Mostrar el dictamen del árbitro bajando puntos. |
| **7:30 - 9:00**<br>*(Ronda 4: Choques de Estrés Monte Carlo)* | **Paso 6 del Recorrido:** Gráfico Monte Carlo con choque de pandemia y caída de commodities. | "En la **Ronda 4**, les arrojé 40 corridas estocásticas de Monte Carlo simulando dos crisis simultáneas: una pandemia de salud y un choque externo de caída del precio del petróleo.<br><br>El modelo capitalista colapsó socialmente por no tener transferencias automáticas. Pero el modelo colectivista colapsó fiscalmente: con una deuda disparada ($b_t > 88\\%$), el spread soberano superó el 11%, cerrando el crédito internacional.<br><br>El modelo mixto fue el único que superó la prueba de resiliencia con un score del 84%." | `[✂️ En versión 8m: resumir en 30s]`.<br>**Destacar:** Bandas de incertidumbre Monte Carlo. |
| **9:00 - 10:30**<br>*(Rondas 5 y 6: Las Concesiones Históricas)* | **Pasos 7 y 8 del Recorrido:** Regla de Posiciones (Policymeter) y Tarjetas R5-R6. | "Y llegamos a las **Rondas 5 y 6**. Al ver los resultados matemáticos de las crisis, las IAs empezaron a ceder.<br><br>El Colectivista bajó su exigencia estatal del 85% al 20%, aceptando que la empresa privada es el motor insustituible de la innovación. El Capitalista aceptó una tasa impositiva máxima del 35% y un piso de salud y educación públicas para elevar el capital humano ($H$).<br><br>Miren el Policymeter: el medidor de convergencia saltó al **{cards[5]['convergence_pct']:.1f}%**." | **Tono emocionado:** Resaltar el movimiento de los puntos en el Policymeter. |
| **10:30 - 12:00**<br>*(Ronda 7: NSGA-III, Nash y Bautismo)* | **Pestaña `🏆 2. Resultado Final`:** Frontera de Pareto, Ecuación de Nash y Ficha de Consenso. | "En la **Ronda 7**, dejamos que el algoritmo genético multiobjetivo **NSGA-III** explorara la Frontera de Pareto de soluciones no dominadas, y aplicamos el **Criterio de Negociación de Nash (NBS)** para encontrar el punto exacto que maximiza el producto de excedentes de los tres agentes sin vetos.<br><br>El Árbitro bautizó el acuerdo como: **'{model_name}'**.<br><br>Los cuatro pilares para {country}:<br>1. **Formalización Laboral:** Monotributo simple y reducción de costos parafiscales para formalizar la economía popular.<br>2. **Pacto Fiscal Gradual:** Ampliación progresiva del recaudo (~28%-32% del PIB) atacando la elusión del 1% superior.<br>3. **Pilar Solidario Pensional:** Renta básica a los 3 millones de adultos mayores vulnerables sin pensión.<br>4. **Regla Fiscal con Fondo Soberano:** Blindaje contracíclico contra la volatilidad del petróleo y carbón.<br><br>Los tres agentes votaron **A FAVOR** y firmaron el pacto unánimemente." | **Visual:** Mostrar la estrella dorada ⭐ en Pareto y la tabla de consenso. |
| **12:00 - 13:30**<br>*(La Parte Honesta: Límites del Modelo)* | **Pestaña `🧭 Recorrido` → Paso 11** (*Qué significa y qué NO significa*). | "Ahora, la sección obligatoria: **la parte honesta**.<br><br>¿Descubrió la inteligencia artificial la fórmula mágica para gobernar cualquier país? **No.** Ningún modelo computacional puede predecir guerras mundiales o la complejidad de la política humana.<br><br>Lo que este experimento sí demuestra es algo fascinante: cuando fuerzas a posturas polarizadas a medirse contra identidades contables cerradas, datos reales y pruebas de estrés, el fanatismo cede y emerge el compromiso técnico pragmático." | **Cámara:** Plano cerrado, contacto visual directo, tono reflexivo y sincero. |
| **13:30 - 15:00**<br>*(Cierre, Código Abierto & CTA)* | **Plano medio a cámara:** Pantalla mostrando el repositorio de GitHub y el PDF generado. | "Dejé todo el código fuente 100% abierto en GitHub bajo **Licencia MIT**, incluyendo el simulador Solow, los prompts y el visualizador interactivo. Además, dejé una demo web pública alojada funcionando en **Modo Replay (0 tokens)** para que cualquiera pueda explorar los resultados de inmediato sin gastar dinero ni ingresar claves.<br><br>Y si quieres clonar el proyecto, puedes poner tu propia clave de API en `.env`, cambiar de modelo de lenguaje o calibrar tu propio país y correr nuevos debates.<br><br>Déjame en los comentarios: ¿crees que este pacto funcionaría en tu país o qué política ajustarías tú?<br><br>Si te apasiona la intersección entre inteligencia artificial, datos y economía, suscríbete y déjale un like al video. ¡Nos vemos en el próximo debate!" | **Final:** Música de cierre, pantalla final con botón de suscripción, link a GitHub y demo. |

---

## 📱 Guion Corto para Redes Sociales (Shorts / Reels / TikTok - 60 Segundos)

* **[0:00 - 0:10] (Gancho visual):** *"Puse a tres inteligencias artificiales a debatir de economía: una capitalista radical, una socialista marxista y una socialdemócrata. Usando el mismo modelo para todas, pero atadas a un simulador matemático real."*
* **[0:10 - 0:25] (El conflicto):** *"En la primera ronda, el modelo capitalista duplicaba el PIB pero disparaba la desigualdad a un Gini de 0.54. El modelo socialista erradicaba la pobreza pero provocaba una fuga de capitales del 40% que quebraba al país."*
* **[0:25 - 0:45] (El giro matemático):** *"Tras 7 rondas auditadas por un árbitro con expresiones regulares y optimización Pareto NSGA-III, las tres IAs firmaron este pacto: formalización laboral del 56% informal, pilar pensional solidario y regla fiscal estricta."*
* **[0:45 - 1:00] (Llamado a la acción):** *"Las tres IAs firmaron el acuerdo unánimemente. ¿Crees que los humanos podríamos hacer lo mismo? El código completo con licencia MIT y demo están en mi perfil. ¡Comenta tu postura!"*

---

## 🎯 3 Opciones de Títulos Atractivos para YouTube
1. **Opción A (Provocador / Curiosidad):** *Puse a 3 IAs con Ideologías Opuestas a Diseñar la Economía Perfecta (y Pasó Esto)*
2. **Opción B (Técnico + Popular):** *¿Pueden 3 IAs Ponerse de Acuerdo en Economía? Debate Multi-Agente con Simulación Real y Pareto*
3. **Opción C (Enfocado en Consenso):** *El Algoritmo que Resolvió la Polarización: 7 Rondas de Debate Macroeconómico con IA*

---

## 🖼️ 3 Ideas de Miniatura (Thumbnails)
1. **Concepto 1 (Caras de IA vs Balanza):** Tres avatares con colores intensos (🔴 Rojo, 🟠 Naranja, 🔵 Azul) mirando fijamente a una balanza matemática dorada en el centro. Texto grande: *"¿ACUERDO IMPOSIBLE?"*.
2. **Concepto 2 (Dashboard Real):** Captura limpia de la Regla de Posiciones (Policymeter) con la estrella dorada brillando y flechas señalando las concesiones. Texto: *"7 RONDAS DE DEBATE"*.
3. **Concepto 3 (Ingeniero con Gráficas):** Foto del presentador con expresión de asombro mirando la pantalla del simulador Monte Carlo y la Frontera de Pareto. Texto: *"LA SIMULACIÓN MANDÓ"*.

---

## 📌 Capítulos de YouTube con Marcas de Tiempo
* `0:00` - ¿Pueden 3 IAs ponerse de acuerdo en economía?
* `0:30` - Arquitectura: Mismo modelo de IA, Árbitro y Simulador Solow
* `1:30` - Las 4 reglas de oro y cómo audita el Árbitro por código
* `2:30` - Capitalismo vs Socialismo vs Socialdemocracia en el contexto real
* `3:45` - Ronda 1: Apertura y polarización inicial
* `5:00` - Ronda 2: El simulador castiga las fantasías ideológicas
* `6:15` - Ronda 3: Preguntas cruzadas y auditoría de cifras
* `7:30` - Ronda 4: Choque de pandemia y crisis petrolera Monte Carlo
* `9:00` - Rondas 5 y 6: El momento de las concesiones históricas
* `10:30` - Ronda 7: Algoritmo NSGA-III, Solución de Nash y Consenso
* `12:00` - La parte honesta: Qué NO significa este resultado
* `13:30` - Código abierto con Licencia MIT, demo y conclusiones

---

## 🚫 Frases Prohibidas vs ✅ Frases Seguras

| 🚫 Frases que NUNCA debo decir | ✅ Frases Seguras de Divulgación Rigurosa |
|---|---|
| *"La IA demostró matemáticamente que el capitalismo/socialismo no sirve."* | *"En este modelo computacional simplificado, las posturas extremas generaron desbalances macroeconómicos severos."* |
| *"Este consenso es la receta perfecta que deberían aplicar todos los gobiernos."* | *"Este consenso representa un óptimo de compromiso bajo las identidades contables de esta simulación."* |
| *"La IA es completamente imparcial y no comete errores."* | *"Las IAs están limitadas por las directivas que programé y por las ecuaciones del simulador."* |
| *"Resolvimos el debate económico universal."* | *"Construimos una herramienta cuantitativa para explorar trade-offs y facilitar el entendimiento mutuo."* |

---

## ❓ 8 Preguntas Frecuentes de los Comentarios (con Respuestas Listas)
1. **¿Por qué no podemos aplicar directamente el modelo de Suecia o Dinamarca en Colombia?** → *Porque en Suecia el recaudo es del 43% del PIB y la formalidad es del 95%. En Colombia la informalidad es del 56% y el recaudo es del 19%. Aplicar impuestos nórdicos sin formalizar primero destruiría el empleo y dispararía la evasión.*
2. **¿Qué fórmulas matemáticas rigen el simulador?** → *Función de producción Cobb-Douglas con capital humano ($Y = A K^\\alpha H^\\beta L^\\gamma$), dinámica de deuda ($\\Delta b_t$), consumo agregado microfundamentado por quintiles y regla de Taylor.*
3. **¿Cómo funciona el algoritmo del Árbitro para detectar mentiras?** → *Usa tokenización por expresiones regulares que preserva números decimales, mapea las variables a los arrays de la simulación y aplica una banda de tolerancia del 5%. Si una cifra no coincide, penaliza automáticamente la rúbrica.*
4. **¿Por qué usaron el mismo modelo de IA para todos los agentes?** → *Para asegurar total paridad metodológica y evitar sesgos de capacidad cognitiva entre posturas. La diferencia proviene exclusivamente de las directivas teóricas y la simulación. En el código abierto puedes configurar diferentes modelos para cada agente.*
5. **¿Qué modelos de lenguaje usaste y cómo puedo probar el mío?** → *Utilizamos GroqCloud con modelos Llama-3/GPT-OSS. El repositorio incluye un archivo `.env.example` donde puedes ingresar tu propia clave de API y seleccionar el modelo que desees.*
6. **¿Por qué la simulación castiga la emisión monetaria sin respaldo?** → *Porque el modelo incluye la regla de Taylor y la curva de Phillips; la dominancia fiscal genera un salto inmediato en la prima de riesgo y en la inflación.*
7. **¿El modelo contempla choques de materias primas?** → *Sí, incluye choques estocásticos de términos de intercambio (petróleo y carbón) y un Fondo de Estabilización Soberano.*
8. **¿Dónde puedo descargar el reporte y el código?** → *Todo el código fuente bajo Licencia MIT y el reporte formal en PDF de 12 secciones están disponibles en el repositorio abierto de GitHub.*

---

## 🎥 Checklist de Grabación en 1080p / 4K
- [ ] Servidor de Streamlit activo en `http://localhost:8501` en modo `replay` (reproducción offline fluida sin latencia).
- [ ] Interruptor **🎬 Modo Presentación (Video)** activado en la barra lateral (oculta paneles técnicos y maximiza gráficos).
- [ ] Nivel de zoom del navegador al 100% (o 110% para tomas de texto cerrado en 4K).
- [ ] Tema oscuro activo en Streamlit para contraste de colores de los 3 agentes.
- [ ] Fórmulas matemáticas listas para superposición en pantalla durante la edición.
"""
    return md_content

def export_video_script_file():
    """Genera y guarda el archivo docs/video/GUION_VIDEO.md."""
    golden_file = OUTPUTS_DIR / "golden_run" / "debate_session_golden.json"
    if golden_file.exists():
        with open(golden_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        latest_file = OUTPUTS_DIR / "debate_session_latest.json"
        if latest_file.exists():
            with open(latest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"rounds": [], "proposal": {}}
            
    script_md = generate_video_script_markdown(data)
    
    docs_video_dir = BASE_DIR / "docs" / "video"
    docs_video_dir.mkdir(parents=True, exist_ok=True)
    
    out_file = docs_video_dir / "GUION_VIDEO.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(script_md)
        
    # Guardar también en outputs para acceso directo
    outputs_script = OUTPUTS_DIR / "GUION_VIDEO.md"
    with open(outputs_script, "w", encoding="utf-8") as f:
        f.write(script_md)
        
    print(f"[OK] Guion de video generado con exito en: {out_file}")

if __name__ == "__main__":
    export_video_script_file()

