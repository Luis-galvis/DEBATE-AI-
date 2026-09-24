"""
Cargador y Gestor del Glosario Central (config/glossary.yaml).
Valida mediante Pydantic y provee helpers para etiquetas dinámicas según nivel de lectura,
tarjetas de ayuda contextual, pies explicativos de gráficos y medición de legibilidad en español.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import re
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[3]
GLOSSARY_PATH = ROOT_DIR / "config" / "glossary.yaml"

class GlossaryEntry(BaseModel):
    """Esquema de una entrada canónica en el glosario."""
    id: str
    nombre_simple: str
    nombre_tecnico: str
    categoria: str
    definicion_corta: str
    analogia_cotidiana: str
    ejemplo_con_datos: str
    como_leerlo: str
    por_que_importa: str
    lo_que_no_mide: str
    sinonimos: List[str] = Field(default_factory=list)
    nivel_de_detalle: str = "simple"  # simple, intermedio, tecnico

class GlossaryDatabase:
    """Base de datos en memoria del glosario validado."""
    def __init__(self, file_path: Path = GLOSSARY_PATH):
        self.entries: Dict[str, GlossaryEntry] = {}
        self._load(file_path)

    def _load(self, file_path: Path):
        if not file_path.exists():
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for item in data.get("glossary", []):
            entry = GlossaryEntry(**item)
            self.entries[entry.id] = entry

    def get(self, term_id: str) -> Optional[GlossaryEntry]:
        """Obtiene una entrada por su ID exacto o por coincidencia en sinónimos."""
        if term_id in self.entries:
            return self.entries[term_id]
        clean_id = term_id.lower().strip()
        for entry in self.entries.values():
            if clean_id in [s.lower() for s in entry.sinonimos]:
                return entry
        return None

    def get_label(self, term_id: str, level: str = "simple") -> str:
        """Devuelve la etiqueta adecuada según el nivel de lectura configurado."""
        entry = self.get(term_id)
        if not entry:
            return term_id.replace("_", " ").capitalize()
        if level == "simple":
            return entry.nombre_simple
        elif level == "intermedio":
            return f"{entry.nombre_simple} ({entry.nombre_tecnico})"
        else:
            return entry.nombre_tecnico

    def get_all(self, category: Optional[str] = None) -> List[GlossaryEntry]:
        """Devuelve todas las entradas, opcionalmente filtradas por categoría."""
        if category and category != "Todas":
            return [e for e in self.entries.values() if e.categoria == category]
        return list(self.entries.values())

    def get_categories(self) -> List[str]:
        """Lista todas las categorías presentes en el glosario."""
        cats = sorted(list(set(e.categoria for e in self.entries.values())))
        return ["Todas"] + cats

_GLOSSARY_INSTANCE: Optional[GlossaryDatabase] = None

def get_glossary() -> GlossaryDatabase:
    """Singleton para acceder a la base de datos del glosario."""
    global _GLOSSARY_INSTANCE
    if _GLOSSARY_INSTANCE is None:
        _GLOSSARY_INSTANCE = GlossaryDatabase()
    return _GLOSSARY_INSTANCE

def format_help_card(term_id: str, dynamic_data: Optional[Dict[str, Any]] = None) -> str:
    """Genera el contenido en Markdown de la tarjeta de ayuda contextual."""
    glossary = get_glossary()
    entry = glossary.get(term_id)
    if not entry:
        return f"**{term_id}**: Sin información detallada en el glosario."

    ejemplo = entry.ejemplo_con_datos
    if dynamic_data:
        try:
            ejemplo = ejemplo.format(**dynamic_data)
        except Exception:
            pass

    return f"""
### 📖 {entry.nombre_simple}
*{entry.nombre_tecnico}* — **{entry.categoria}**

- 💡 **En una frase:** {entry.definicion_corta}
- 🍕 **Analogía cotidiana:** {entry.analogia_cotidiana}
- 🧭 **Cómo interpretarlo:** {entry.como_leerlo}
- 🌟 **Por qué importa:** {entry.por_que_importa}
- ⚠️ **Lo que NO mide:** {entry.lo_que_no_mide}
- 📊 **En este modelo:** {ejemplo}
"""

def generate_chart_footer(
    chart_id: str,
    context_data: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Genera los tres bloques de texto explicativo ('Qué estás viendo', 'Cómo leerlo', 'Ojo con esto')
    rellenados deterministamente con números del modelo.
    """
    data = context_data or {}
    
    footers = {
        "pca_trajectories": {
            "what_you_see": "Estás viendo cómo se movieron las propuestas de los tres agentes a lo largo de las 7 rondas hasta acordar el punto medio.",
            "how_to_read": "Cada punto es una ronda. Cuanto más cerca están los puntos entre sí, mayor es el acuerdo entre las posturas.",
            "watch_out": "Es una proyección 2D simplificada de 10 decisiones de política; resume la cercanía pero simplifica detalles.",
        },
        "trajectories_30y": {
            "what_you_see": "Estás viendo la evolución proyectada año a año durante los próximos 30 años bajo cada paquete de políticas.",
            "how_to_read": "La línea dorada representa el Consenso. Compara si logra estabilidad sin caídas abruptas.",
            "watch_out": "Es una simulación matemática continua que asume cumplimiento de reglas fiscales y no incluye shocks imprevisibles fuera de los 7 escenarios.",
        },
        "radar_multidim": {
            "what_you_see": "Estás viendo una comparación simultánea de las 4 posiciones en 8 dimensiones clave (salud, empleo, igualdad, solvencia, etc.).",
            "how_to_read": "Cuanto más amplia y equilibrada sea la figura geométrica, más balanceado y completo es el desempeño del modelo.",
            "watch_out": "Todas las variables están normalizadas a escala 0-100; tener una punta alta en una esquina suele implicar sacrificios en otra.",
        },
        "pareto_cloud": {
            "what_you_see": "Estás viendo la nube de las mejores combinaciones posibles encontradas por el algoritmo entre cientos de opciones evaluadas.",
            "how_to_read": "Los puntos marcados muestran dónde se ubican los métodos de compromiso (TOPSIS, Nash, etc.) respecto a los extremos.",
            "watch_out": "Cualquier punto en el borde es técnicamente eficiente; la elección final depende de los valores éticos y prioridades de cada sociedad.",
        },
        "concessions_bars": {
            "what_you_see": "Estás viendo cuánto cedió cada agente en cada uno de los 10 parámetros respecto a su postura inicial de partida.",
            "how_to_read": "Barras hacia la derecha indican aumentos de intervención o gasto; barras hacia la izquierda indican desregulación o apertura.",
            "watch_out": "Las barras en cero representan las líneas rojas y principios doctrinarios que cada agente no estuvo dispuesto a negociar.",
        },
    }
    
    default_footer = {
        "what_you_see": "Estás viendo los resultados comparados de las 4 posturas económicas evaluadas por el simulador.",
        "how_to_read": "Compara las diferencias relativas entre modelos y la ubicación del consenso final.",
        "watch_out": "Los resultados provienen de un modelo matemático simplificado para fines educativos y de divulgación.",
    }
    
    return footers.get(chart_id, default_footer)

def calculate_readability_score(text: str) -> Dict[str, Any]:
    """
    Calcula el índice de legibilidad de Fernández-Huerta y la escala INFLESZ para textos en español.
    Fórmula Fernández-Huerta: L = 206.84 - (0.60 * P) - (1.02 * F)
    donde:
      P = sílabas por cada 100 palabras (n_syllables / n_words * 100)
      F = promedio de palabras por frase (n_words / n_sentences)
    """
    words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+\b', text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    n_words = len(words)
    n_sentences = max(1, len(sentences))
    
    if n_words == 0:
        return {"score": 100.0, "level": "Muy Fácil", "inflesz": "Muy Fácil"}
        
    # Estimación de sílabas en español reduciendo diptongos
    t_clean = text.lower()
    t_clean = re.sub(r'[aeoáéó][iuü]|ui|[iuü][aeoáéó]|[iuü][iuü]', 'a', t_clean)
    vowels = re.findall(r'[aeiouáéíóúü]', t_clean)
    n_syllables = max(n_words, len(vowels))
    
    p = (n_syllables / n_words) * 100.0
    f = n_words / n_sentences  # Longitud media de la frase
    
    score = 206.84 - (0.60 * p) - (1.02 * f)
    score = max(0.0, min(100.0, score))
    
    # Escala INFLESZ / Fernández-Huerta
    if score >= 80:
        level = "Muy Fácil (Primaria)"
    elif score >= 65:
        level = "Fácil (Secundaria Básica)"
    elif score >= 55:
        level = "Normal (Público General / Bachillerato)"
    elif score >= 40:
        level = "Algo Difícil (Universitario)"
    else:
        level = "Muy Técnico / Difícil"
        
    return {
        "score": round(score, 1),
        "level": level,
        "is_acceptable": score >= 50.0,
        "words_count": n_words,
        "sentences_count": n_sentences,
    }
