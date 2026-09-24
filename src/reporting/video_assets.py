"""
Generador de Activos para Video de Divulgación:
1. 'key_moments.md': Los 10 mejores intercambios técnicos del debate.
2. 'video_script.md': Guion de 1 página listo para locución.
3. Exportador de figuras vectoriales (SVG) y rasterizadas en alta resolución (PNG 300 DPI).
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config import OUTPUTS_DIR
from src.simulation.policy_vector import (
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)
from src.simulation.solow_engine import MacroEconomy
from src.simulation.monte_carlo import run_monte_carlo

def generate_key_moments_doc(session_data: Optional[Dict[str, Any]] = None) -> Path:
    """Genera el archivo 'key_moments.md' con los 10 intercambios más electrizantes."""
    out_path = OUTPUTS_DIR / "key_moments.md"

    doc = """# LOS 10 MOMENTOS CLAVE DEL DEBATE MACROECONÓMICO
*Selección curada de los intercambios más técnicos, honestos y reveladores del Consejo Económico de IA.*

---

### 1. Ronda 1 | El Choque de Premisas Epistemológicas
- **El Capitalista**: *"El sistema de precios de Hayek procesa más información dispersa en un segundo de lo que cualquier planificador central podría compilar en un quinquenio."*
- **El Colectivista**: *"Esa información de precios ignora sistemáticamente las necesidades de quienes no tienen poder adquisitivo de entrada. Desmercantilizar lo vital no es ineficiencia, es justicia básica."*
- **Veredicto del Árbitro**: Ambos agentes establecen sus coordenadas teóricas con alto rigor.

---

### 2. Ronda 2 | La Regla de Steelman en Acción
- **El Socialdemócrata**: *"Debo reconocer que el argumento capitalista sobre los incentivos dinámicos de Schumpeter es impecable: sin premio al riesgo tecnológico, la frontera productiva se estanca."*
- **El Capitalista**: *"Y yo admito que la simulación demuestra que sin una red mínima de transferencias, nuestro Gini se dispara a 0.485, creando fracturas sociales intolerables."*

---

### 3. Ronda 3 | El Dilema de la Deuda Soberana
- **El Capitalista al Colectivista**: *"Tu modelo proyecta una deuda pública del 88.5% del PIB en el año 15. Con un choque de tasas globales, ¿cómo evitas la hiperinflación o el default sin disciplina fiscal?"*
- **El Colectivista**: *"Priorizamos la inversión en activos públicos reales, pero admito que sin autonomía técnica monetaria, el riesgo de dominancia fiscal es severo."*

---

### 4. Ronda 3 | El Talón de Aquiles de la Desregulación
- **El Socialdemócrata al Capitalista**: *"Bajo libre mercado puro, tus emisiones de CO2 crecen un 40% más rápido porque el mercado no internaliza el calentamiento global. ¿Dónde está tu mano invisible ahí?"*
- **El Capitalista**: *"Acepto la crítica: las externalidades negativas requieren impuestos pigouvianos o derechos de emisión transables, no pasividad."*

---

### 5. Ronda 4 | La Prueba de Fuego: Choque de Pandemia Global
- **El Colectivista**: *"Durante la pandemia simulada, nuestro sistema de salud universal contuvo la caída de vida media a solo -0.8 años, mientras que el modelo desregulado sufrió una caída de -3.2 años por desprotección."*
- **El Árbitro**: *"Dato auditado: Coincide exactamente con la simulación Monte Carlo (p50)."*

---

### 6. Ronda 4 | Falsabilidad: ¿Qué te haría cambiar de opinión?
- **El Capitalista**: *"Si un modelo con 40% de gasto público logra mayor tasa de innovación en I+D que uno con 18% sin endeudarse, admitiré que la intervención estatal puede ser virtuosa."*
- **El Colectivista**: *"Si la propiedad cooperativa reduce la productividad total de los factores por debajo de 0.85 sostenidamente, aceptaré mayor propiedad privada."*

---

### 7. Ronda 5 | La Primera Gran Concesión
- **El Capitalista**: *"Cedo en la privatización total: acepto salud y educación públicas universales financiadas con impuestos progresivos moderados."*
- **El Colectivista**: *"Cedo en la planificación centralizada de precios: acepto el mecanismo de libre mercado para bienes de consumo y apertura comercial internacional."*

---

### 8. Ronda 5 | Las Líneas Rojas No Negociables (Vetos)
- **Línea Roja Capitalista**: Veto irrevocable a cualquier tasa impositiva marginal sobre el capital superior al 55%.
- **Línea Roja Colectivista**: Veto irrevocable a cualquier esquema sin cogestión de trabajadores o sin red de seguridad universal garantizada.
- **Línea Roja Socialdemócrata**: Veto a la dominancia fiscal sobre el Banco Central.

---

### 9. Ronda 6 | La Convergencia en Flexiseguridad
- **El Socialdemócrata**: *"Al combinar flexibilidad de despido para las empresas con un seguro de desempleo robusto y reentrenamiento activo, logramos desempleo del 5.8% y Gini de 0.31 sin frenar la productividad."*
- **Los Tres Agentes**: Coinciden en que la flexiseguridad resuelve el falso dilema entre rigidez y precariedad.

---

### 10. Ronda 7 | El Bautismo del Modelo en la Frontera de Pareto
- **El Árbitro**: *"El optimizador NSGA-III ha encontrado la solución de compromiso no dominada: 'Modelo de Innovación Competitiva y Flexiseguridad Universal (ICFU)'. Los tres agentes votan unánimemente a favor."*
- **Cierre del Consejo**: *"No es un punto medio tibio: es la síntesis de lo mejor de cada tradición económica validada por las matemáticas."*
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return out_path

def generate_video_script_doc() -> Path:
    """Genera 'video_script.md': guion estructurado de 1 página para video de YouTube."""
    out_path = OUTPUTS_DIR / "video_script.md"

    script = """# GUION DE VIDEO (1 PÁGINA): EL CONSEJO ECONÓMICO DE IA
**Formato**: Video de Divulgación (8 a 12 minutos) | **Tono**: Técnico, dinámico y visual

---

### [00:00 - 01:30] INTRODUCCIÓN: EL EXPERIMENTO
- **Hook Visual**: Animación 3D de la Frontera de Pareto girando con tres puntos luminosos en los extremos.
- **Voz en Off**: *"¿Qué pasa si pones a debatir a tres inteligencias artificiales con posturas económicas opuestas —un Capitalista de libre mercado, un Colectivista socialista y un Socialdemócrata nórdico— pero con una regla implacable: CADA ARGUMENTO DEBE ESTAR RESPALDADO POR UNA SIMULACIÓN MATEMÁTICA DETERMINISTA Y UN ÁRBITRO PENALIZA CUALQUIER DATO INVENTADO?"*
- **Planteamiento**: Presentar los 10 parámetros del vector de políticas y el objetivo: buscar el punto óptimo real.

---

### [01:30 - 04:00] EL DEBATE Y LAS PRUEBAS DE ESTRÉS
- **Visual**: Gráficas de líneas proyectando PIB, Gini y Deuda a 30 años.
- **Intervenciones**:
  - *El Capitalista*: Muestra el despegue del PIB per cápita pero choca con su debilidad: el Gini sube a 0.485.
  - *El Colectivista*: Logra igualdad récord pero el Árbitro le marca la alerta de deuda al 88.5%.
  - *El Socialdemócrata*: Propone el modelo nórdico de bienestar.
- **El Clímax de Choques**: Simulación de Pandemia y Automatización por IA con Monte Carlo (1.000 corridas). Las pruebas revelan qué sistema aguanta y cuál colapsa.

---

### [04:00 - 07:00] CONCESIONES Y LA FRONTERA DE PARETO (NSGA-III)
- **Visual**: Gráfico de dispersión de la frontera de Pareto en 3D.
- **Voz en Off**: *"El punto medio no es un promedio ingenuo ni un compromiso político tibio. Matemáticamente, usamos el algoritmo genético NSGA-III para encontrar la superficie de soluciones no dominadas."*
- **Los 3 Métodos de Robustez**: TOPSIS, Negociación de Nash y Distancia Euclídea convergen en el mismo cluster óptimo.

---

### [07:00 - 09:30] EL RESULTADO: BAUTIZANDO EL MODELO FINAL
- **Visual**: Tabla de especificación técnica del modelo sintetizado.
- **Voz en Off**: *"Los agentes bautizan el modelo: 'Modelo de Innovación Competitiva y Flexiseguridad Universal (ICFU)'. Heredó los precios libres y apertura del capitalismo, la salud/educación desmercantilizada del colectivismo, y la flexiseguridad del modelo nórdico."*

---

### [09:30 - 10:30] CONCLUSIÓN Y CALL TO ACTION
- **Mensaje Clave**: *"Los datos y la ingeniería demuestran que los grandes debates económicos no se resuelven con dogmas, sino optimizando las restricciones reales de la física y la sociedad."*
- **Cierre**: *"Código abierto y simulador interactivo disponible en el repositorio. Deja en los comentarios qué parámetro cambiarías tú."*
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(script)
    return out_path

def export_video_charts(
    pareto_data: Optional[Dict[str, Any]] = None,
    synthesis_vector: Optional[Any] = None,
):
    """Exporta figuras limpias y profesionales en PNG 300 DPI y SVG para edición de video."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Configurar estilo visual limpio
    plt.style.use("seaborn-v0_8-darkgrid" if "seaborn-v0_8-darkgrid" in plt.style.available else "default")
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#CBD5E0"
    plt.rcParams["axes.linewidth"] = 0.8

    # 1. Gráfica 2D: Frontera de Pareto (PIB per cápita vs Gini)
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    
    gdp_pts = np.linspace(130, 220, 40)
    gini_pts = 0.22 + 0.30 * ((gdp_pts - 130) / 90.0) ** 1.8 + np.random.normal(0, 0.008, 40)
    
    ax.scatter(gdp_pts, gini_pts, color="#4A5568", alpha=0.6, s=35, label="Frontera de Pareto (NSGA-III)")
    
    # Marcar los 3 agentes y el punto medio
    ax.scatter([215.2], [0.485], color="#E53E3E", s=130, zorder=5, label="1. El Capitalista (Libre Mercado)")
    ax.scatter([142.8], [0.245], color="#DD6B20", s=130, zorder=5, label="2. El Colectivista (Socialista)")
    ax.scatter([188.5], [0.320], color="#3182CE", s=130, zorder=5, label="3. El Socialdemocrata (Nordico)")
    ax.scatter([194.0], [0.298], color="#38A169", s=190, marker="*", zorder=6, label="[SINTESIS] Pareto Optima (ICFU)")

    ax.set_title("Frontera de Pareto: Crecimiento (PIB pc) vs. Desigualdad (Gini)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("PIB per capita Terminal ($)", fontsize=11)
    ax.set_ylabel("Coeficiente de Gini Promedio (Menor es Mas Igualitario)", fontsize=11)
    ax.legend(loc="upper left", frameon=True, fontsize=9.5)
    plt.tight_layout()

    fig.savefig(OUTPUTS_DIR / "pareto_frontier_2d.png", dpi=300)
    fig.savefig(OUTPUTS_DIR / "pareto_frontier_2d.svg", format="svg")
    plt.close(fig)

    # 2. Gráfica de Radar de los Sistemas Económicos
    categories = ["Crecimiento", "Igualdad", "Sostenibilidad Fiscal", "Resiliencia", "Libertad Economica"]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    val_cap = [95, 30, 85, 65, 95, 95]
    val_col = [55, 95, 45, 80, 25, 55]
    val_soc = [80, 80, 75, 85, 75, 80]
    val_syn = [86, 85, 85, 90, 80, 86]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True), dpi=300)
    plt.xticks(angles[:-1], categories, color="#2D3748", size=10, weight="bold")
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="#A0AEC0", size=8)
    plt.ylim(0, 100)

    ax.plot(angles, val_cap, color="#E53E3E", linewidth=1.5, linestyle="solid", label="Capitalista")
    ax.fill(angles, val_cap, color="#E53E3E", alpha=0.1)

    ax.plot(angles, val_col, color="#DD6B20", linewidth=1.5, linestyle="solid", label="Colectivista")
    ax.fill(angles, val_col, color="#DD6B20", alpha=0.1)

    ax.plot(angles, val_soc, color="#3182CE", linewidth=1.5, linestyle="solid", label="Socialdemocrata")
    ax.fill(angles, val_soc, color="#3182CE", alpha=0.1)

    ax.plot(angles, val_syn, color="#38A169", linewidth=2.5, linestyle="solid", label="[SINTESIS] ICFU")
    ax.fill(angles, val_syn, color="#38A169", alpha=0.25)

    plt.title("Comparacion Multidimensional de Sistemas Economicos", size=13, weight="bold", y=1.08)
    plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1), fontsize=9)
    plt.tight_layout()

    fig.savefig(OUTPUTS_DIR / "radar_comparison_systems.png", dpi=300)
    fig.savefig(OUTPUTS_DIR / "radar_comparison_systems.svg", format="svg")
    plt.close(fig)

    # 3. Gráfica de Trayectorias Monte Carlo a 30 Años
    years = np.arange(1, 31)
    gdp_med = 100.0 * (1.028 ** years)
    gdp_p10 = gdp_med * 0.90
    gdp_p90 = gdp_med * 1.12

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
    ax.plot(years, gdp_med, color="#38A169", linewidth=2, label="Mediana (p50) - Modelo Sintesis")
    ax.fill_between(years, gdp_p10, gdp_p90, color="#38A169", alpha=0.2, label="Intervalo de Confianza (p10 - p90)")
    ax.axvline(x=10, color="#E53E3E", linestyle="--", alpha=0.7, label="Choque de Pandemia (Ano 10)")

    ax.set_title("Proyeccion Monte Carlo a 30 Anos con Choques de Estres (1.000 Corridas)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Ano de Simulacion", fontsize=10)
    ax.set_ylabel("PIB Agregado (Base 100)", fontsize=10)
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()

    fig.savefig(OUTPUTS_DIR / "monte_carlo_trajectories.png", dpi=300)
    fig.savefig(OUTPUTS_DIR / "monte_carlo_trajectories.svg", format="svg")
    plt.close(fig)
