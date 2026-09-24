# Supuestos Macroeconómicos, Ecuaciones y Límites Epistemológicos (ASSUMPTIONS.md)

> **AVISO IMPORTANTE**: Este sistema constituye un modelo computacional simplificado con fines educativos y de divulgación sobre ingeniería de IA, optimización multiobjetivo y economía política. Las simulaciones y resultados sintetizados no constituyen asesoría ni recomendaciones directas de política pública para ninguna jurisdicción real.

---

## 1. Fundamentos Teóricos del Motor Macroeconómico

### 1.1 Función de Producción Agregada (Solow-Swan Ampliado con Capital Humano)
El producto interior bruto $Y_t$ en el periodo $t$ se determina mediante una función de producción Cobb-Douglas con rendimientos constantes a escala:

$$Y_t = A_t K_t^\alpha H_t^\beta L_{\text{eff}, t}^{1 - \alpha - \beta}$$

Donde:
- $\alpha = 0.30$: Elasticidad del producto respecto al capital físico $K_t$.
- $\beta = 0.25$: Elasticidad del producto respecto al capital humano $H_t$.
- $1 - \alpha - \beta = 0.45$: Elasticidad del producto respecto al trabajo efectivo $L_{\text{eff}, t} = L_t (1 - u_t)$.
- $A_t$: Productividad Total de los Factores (TFP).

### 1.2 Dinámica de Acumulación y Productividad (TFP)
$$A_{t+1} = A_t \cdot \left(1 + g_{A,0} + \eta_{RD} \cdot \left(\frac{I_{RD,t}}{Y_t}\right) + \eta_{\text{trade}} \cdot \text{TradeOpenness}_t - \eta_{\text{reg}} \cdot \text{MarketRegulation}_t^2\right)$$

- $K_{t+1} = K_t (1 - \delta_K) + I_t$, con $\delta_K = 0.05$.
- $H_{t+1} = H_t (1 - \delta_H) + \psi \cdot (G_{\text{edu\_health}, t})^{0.55}$, con $\delta_H = 0.02$.

### 1.3 Cierre Contable Exacto de la Economía
$$Y_t = C_t + I_t + G_t + NX_t$$

El consumo total de los hogares $C_t$ se calcula mediante la desagregación en 5 quintiles de ingreso ($Q_1 \dots Q_5$) con propensiones marginales decrecientes a consumir:
$$C_t = \sum_{i=1}^5 MPC_i \cdot Y_{d, i, t} \quad \text{con} \quad MPC = [0.96, 0.88, 0.78, 0.68, 0.52]$$

Donde el ingreso disponible por quintil $Y_{d, i}$ incorpora la incidencia progresiva de impuestos (índice Kakwani) y la recepción de transferencias sociales y provisión de bienes públicos.

### 1.4 Dinámica de la Deuda Pública y Prima de Riesgo
$$D_{t+1} = D_t (1 + r_{\text{sovereign}, t}) - PB_t$$
$$r_{\text{sovereign}, t} = r_{\text{world}} + \text{Spread}_t(D_t / Y_t, \text{FiscalRule}, \text{CB\_Independence})$$

El balance primario $PB_t = T_t - G_t - \text{Transfers}_t$. Si la deuda supera el 70% del PIB, el parámetro `fiscal_rule_strictness` activa mecanismos de ajuste primario para contener la divergencia explosiva.

### 1.5 Inflación y Mercado Laboral (Curva de Phillips Aceleracionista)
$$\pi_t = \pi_t^e - \gamma (u_t - u_n) + \text{Shock}_t$$

La tasa natural de desempleo ($u_n$) está determinada por la rigidez del mercado laboral (`labor_protection`) y la carga regulatoria, mientras que la credibilidad del Banco Central ancla las expectativas inflacionarias $\pi_t^e$.

---

## 2. Los 10 Parámetros del Vector de Políticas ($X \in [0, 1]^{10}$)

Todos los parámetros residen exclusivamente en `config/economic_parameters.yaml` y son validados mediante esquemas Pydantic:

| Índice | Dimensión | Rango Normalizado $[0, 1]$ | Mapeo a Tasa Real |
| :---: | :--- | :---: | :--- |
| 0 | `state_ownership` | $0.0 \dots 1.0$ | $0\% \dots 90\%$ de propiedad estatal de activos productivos |
| 1 | `max_tax_rate` | $0.0 \dots 1.0$ | $10\% \dots 75\%$ tasa marginal máxima renta/capital |
| 2 | `tax_progressivity` | $0.0 \dots 1.0$ | Progresividad Kakwani ($0.05 \dots 0.50$) |
| 3 | `public_spending_gdp` | $0.0 \dots 1.0$ | $12\% \dots 60\%$ del PIB en gasto gubernamental |
| 4 | `social_transfers_coverage` | $0.0 \dots 1.0$ | $10\% \dots 70\%$ del gasto dirigido a transferencias/seguro |
| 5 | `market_regulation` | $0.0 \dots 1.0$ | Índice de regulación de mercados / antimonopolio |
| 6 | `labor_protection` | $0.0 \dots 1.0$ | Rigidez laboral, salario mínimo y poder sindical |
| 7 | `trade_openness` | $0.0 \dots 1.0$ | $10\% \dots 95\%$ apertura comercial y de capitales |
| 8 | `fiscal_rule_strictness` | $0.0 \dots 1.0$ | Rigor de regla fiscal anti-déficit y tope de deuda |
| 9 | `central_bank_independence` | $0.0 \dots 1.0$ | Autonomía técnica del Banco Central y meta de inflación |

---

## 3. Los 7 Escenarios de Choque para Pruebas de Estrés

1. **Línea Base Estable**: Evolución normal sin perturbaciones exógenas por 30 años.
2. **Recesión Global Sincronizada**: Caída de demanda externa y términos de intercambio en años 6-8 y 20-21.
3. **Choque de Precios de Commodities**: Contracción de 25% en términos de intercambio para economías exportadoras en años 8-12.
4. **Pandemia Global**: Disrupción de oferta y demanda laboral, gasto extraordinario de salud y contracción en años 10-12.
5. **Envejecimiento Demográfico Acelerado**: Caída gradual del crecimiento de la fuerza de trabajo activa y presión pensional.
6. **Disrupción Tecnológica por IA**: Salto masivo en TFP (+4.5%) con reacomodación estructural del empleo y tensión distributiva.
7. **Crisis de Confianza en Deuda Soberana**: Disparo en primas de riesgo (+650 bps) y corte súbito de financiamiento externo.

---

## 4. Optimización Multiobjetivo y Síntesis de Pareto

Se evalúan 5 objetivos contrapuestos con el algoritmo **NSGA-III** de `pymoo` (con `Das-Dennis` reference directions $P=15$, `pop_size=20`, `n_gen=15`):
1. **Maximizar PIB per cápita terminal** ($f_1$).
2. **Minimizar Desigualdad (Gini promedio)** ($f_2$).
3. **Minimizar Deuda Pública / PIB máxima** ($f_3$).
4. **Maximizar Resiliencia ante Choques** ($f_4$).
5. **Maximizar Bienestar Social y Calidad de Vida** ($f_5$).

### 4.1 Métodos de Síntesis de Compromiso Evaluados
Para garantizar que el vector de compromiso no sea un artefacto de una única fórmula geométrica, el sistema evalúa 5 métodos axiomáticos:
- **TOPSIS**: Proximidad relativa a la solución ideal positiva normalizada en la frontera de Pareto.
- **Nash Bargaining Solution**: $\max \prod_{i=1}^3 (U_i(x) - D_i)_+$ donde $U_i$ es la utilidad del agente $i$ y $D_i$ es su punto de desacuerdo (mínimo histórico o nadir).
- **Kalai-Smorodinsky**: Solución que mantiene la proporcionalidad de las máximas ganancias posibles relativas a la utopía $\frac{U_i - D_i}{U_j - D_j} = \frac{U_i^{max} - D_i}{U_j^{max} - D_j}$.
- **Knee Point (Max-Min Marginal)**: Selección del punto de la frontera donde el intercambio marginal entre objetivos es máximo (máxima curvatura).
- **Distancia Euclídea Ponderada**: Distancia euclídea normalizada respecto al vector utópico $(1, 0, 0, 1, 1)$.

Los puntos utopía y nadir se extraen empíricamente de la propia frontera de Pareto calculada:
- **Utopía**: $z^* = (\max f_1, \min f_2, \min f_3, \max f_4, \max f_5)$
- **Nadir**: $z^{nad} = (\min f_1, \max f_2, \max f_3, \min f_4, \min f_5)$

---

## 5. Verificación de Afirmaciones Cuantitativas por Código

El Árbitro incluye un motor de auditoría determinista (`ArbitrationReferee.verify_claims_against_simulation`) con las siguientes reglas:
1. **Extracción**: Identificación de valores numéricos asociados a métricas clave (`gdp_pc`, `gini`, `debt_gdp`, `resilience`, `welfare`) mediante expresiones regulares insensibles a puntuación flotante.
2. **Tolerancia**: Margen de error aceptable fijado en $\epsilon = \pm 5\%$ del valor real simulado.
3. **Penalización**: Afirmaciones con discrepancias $> 5\%$ o menciones de variables inexistentes son marcadas como `FALSE_CLAIM` y conllevan una deducción de 2.0 puntos en el criterio de rigurosidad empírica de la rúbrica Pydantic.

---

## 6. Limitaciones Conocidas y Sesgos de los Modelos de Lenguaje

### 6.1 Supuestos Estructurales del Simulador
- La economía asume agregación macroeconómica donde los choques se propagan de manera determinista por ecuaciones diferenciales discretizadas anualmente.
- No modela micro-decisiones de portafolio especulativo de alta frecuencia ni mercados bursátiles diarios.

### 6.2 Sesgo por Modelo Base Compartido en los Agentes
> [!IMPORTANT]
> **Aviso sobre Arquitectura de los Agentes**:
> Los tres debatientes ("El Capitalista", "El Colectivista" y "El Socialdemócrata") y el Árbitro utilizan como motor cognitivo el mismo modelo base (`openai/gpt-oss-120b`), condicionado mediante diferentes directivas de sistema (*system prompts*), filosofías económicas y perfiles de temperatura.
>
> **Implicación epistemológica**:
> Aunque cada agente adopta y defiende con vigor su marco teórico (Hayek vs Marx vs Keynes), el modelo base subyacente comparte los mismos pesos pre-entrenados y representaciones del lenguaje. Esto puede inducir un sesgo latente hacia estilos argumentativos similares o concesiones homogéneas. Para mitigar esto, el sistema impone **vetos obligatorios**, **líneas rojas explícitas** y ancla todo el debate en los resultados matemáticos deterministas del simulador numérico.
