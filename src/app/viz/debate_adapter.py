"""
Adaptador de Datos del Debate: Transforma el archivo debate_session.json en estructuras
para visualización de diálogos, PCA 2D, coordenadas paralelas, distancias y rúbricas.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.config import OUTPUTS_DIR
from src.simulation.policy_vector import (
    POLICY_DIMENSIONS,
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)
from src.app.viz.metrics_catalog import COLOR_PALETTE, SYSTEM_LABELS

def _normalize_session_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza sesiones de debate (history, rounds con turns, o rounds con speeches)
    al formato estándar con 'rounds' y lista de 'speeches' estructurados."""
    if not isinstance(raw_data, dict):
        return {"metadata": {}, "rounds": [], "synthesis": None}
        
    # Si ya tiene 'rounds' y cada round tiene 'speeches' no vacíos:
    if "rounds" in raw_data and isinstance(raw_data["rounds"], list) and len(raw_data["rounds"]) > 0:
        first_round = raw_data["rounds"][0]
        if isinstance(first_round, dict) and "speeches" in first_round and first_round["speeches"]:
            if "proposal" in raw_data and "synthesis" not in raw_data:
                raw_data["synthesis"] = {"consensus_vector": raw_data["proposal"].get("policy_vector", {})}
            elif "proposal" in raw_data and isinstance(raw_data.get("synthesis"), dict):
                if "consensus_vector" not in raw_data["synthesis"]:
                    raw_data["synthesis"]["consensus_vector"] = raw_data["proposal"].get("policy_vector", {})
            return raw_data

    # Extraer todos los turnos/items de diálogo
    history = []
    if "history" in raw_data and isinstance(raw_data["history"], list) and raw_data["history"]:
        history = raw_data["history"]
    elif "rounds" in raw_data and isinstance(raw_data["rounds"], list):
        for r_dict in raw_data["rounds"]:
            if isinstance(r_dict, dict):
                r_num = r_dict.get("round", r_dict.get("round_number", 1))
                r_title = r_dict.get("title", r_dict.get("round_name", f"Ronda {r_num}"))
                turns = r_dict.get("turns", r_dict.get("speeches", []))
                for t in turns:
                    if isinstance(t, dict):
                        item = dict(t)
                        item.setdefault("round", r_num)
                        item.setdefault("title", r_title)
                        history.append(item)
                        
    if not history:
        return raw_data
        
    rounds_map = {}
    speaker_id_map = {
        "el capitalista": "capitalist",
        "capitalista": "capitalist",
        "el colectivista": "collectivist",
        "colectivista": "collectivist",
        "el socialdemócrata": "socdem",
        "el socialdemocrata": "socdem",
        "socialdemócrata": "socdem",
        "socialdemocrata": "socdem",
        "árbitro": "referee",
        "arbitro": "referee",
        "referee": "referee",
    }
    
    for item in history:
        r_num = item.get("round", 1)
        if r_num not in rounds_map:
            rounds_map[r_num] = {
                "round_number": r_num,
                "round_name": item.get("title", f"Ronda {r_num}"),
                "focus": item.get("title", "Discusión General"),
                "speeches": [],
                "referee_evaluation": {},
            }
            
        sp_name = item.get("speaker", item.get("speaker_name", "")).lower().strip()
        agent_id = item.get("agent") or speaker_id_map.get(sp_name, "unknown")
        
        speech_obj = {
            "agent": agent_id,
            "speaker_name": item.get("speaker", item.get("speaker_name", "")),
            "content": item.get("content", ""),
            "current_vector": item.get("vector", item.get("current_vector", item.get("adjusted_vector", {}))),
            "claims": item.get("claims", []),
            "evaluation": item.get("evaluation", {}),
        }
        rounds_map[r_num]["speeches"].append(speech_obj)
        
        # Si tiene evaluación del árbitro
        if item.get("evaluation"):
            eval_data = item["evaluation"]
            ref = rounds_map[r_num]["referee_evaluation"]
            if "rubric_scores" not in ref:
                ref["rubric_scores"] = {}
            ref["rubric_scores"][agent_id] = {
                "empirical_rigor": eval_data.get("rigor_score", 8.0),
                "theoretical_coherence": eval_data.get("evidence_score", 8.0),
                "steelman_score": eval_data.get("steelman_score", 8.0),
                "falsifiability_score": eval_data.get("rebuttal_score", 8.0),
                "total_score": eval_data.get("total_score", 8.0),
            }
            ref["summary"] = eval_data.get("feedback", "Evaluación completada.")
            
    sorted_rounds = [rounds_map[k] for k in sorted(rounds_map.keys())]
    raw_data["rounds"] = sorted_rounds
    
    # Normalizar synthesis y proposal
    if "proposal" in raw_data and "synthesis" not in raw_data:
        raw_data["synthesis"] = {"consensus_vector": raw_data["proposal"].get("policy_vector", {})}
    elif "proposal" in raw_data and isinstance(raw_data.get("synthesis"), dict):
        if "consensus_vector" not in raw_data["synthesis"]:
            raw_data["synthesis"]["consensus_vector"] = raw_data["proposal"].get("policy_vector", {})
        
    return raw_data

def load_debate_session_data(filepath: Optional[Path] = None) -> Dict[str, Any]:
    """Carga los datos de la sesión de debate más reciente o del archivo especificado."""
    if filepath and filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return _normalize_session_data(json.load(f))
    
    latest_file = OUTPUTS_DIR / "debate_session_latest.json"
    if latest_file.exists():
        with open(latest_file, "r", encoding="utf-8") as f:
            return _normalize_session_data(json.load(f))
    
    golden_file = OUTPUTS_DIR / "golden_run" / "debate_session_golden.json"
    if golden_file.exists():
        with open(golden_file, "r", encoding="utf-8") as f:
            return _normalize_session_data(json.load(f))
            
    # Fallback con estructura mínima para evitar pantallas rotas
    return {
        "metadata": {"calibration_country": "Colombia", "rounds_completed": 0},
        "rounds": [],
        "synthesis": None
    }

def get_rounds_count(session_data: Dict[str, Any]) -> int:
    """Devuelve el número total de rondas disponibles en la sesión."""
    return len(session_data.get("rounds", []))

def extract_round_dialogues(session_data: Dict[str, Any], round_num: int) -> Dict[str, Any]:
    """Extrae las intervenciones y evaluaciones de una ronda específica (1-indexed)."""
    rounds = session_data.get("rounds", [])
    if not rounds or round_num < 1 or round_num > len(rounds):
        return {"round_number": round_num, "name": f"Ronda {round_num}", "speeches": [], "referee": {}}
    
    target_round = rounds[round_num - 1]
    speeches = []
    
    for speech in target_round.get("speeches", []):
        agent_id = speech.get("agent", "unknown")
        speeches.append({
            "agent_id": agent_id,
            "agent_name": SYSTEM_LABELS.get(agent_id, agent_id.capitalize()),
            "content": speech.get("content", ""),
            "claims": speech.get("claims", []),
            "current_vector": speech.get("current_vector", {}),
            "color": COLOR_PALETTE.get(agent_id, "#A0AEC0"),
            "avatar": {"capitalist": "🔴", "collectivist": "🟠", "socdem": "🔵"}.get(agent_id, "👤"),
        })
        
    return {
        "round_number": round_num,
        "name": target_round.get("round_name", f"Ronda {round_num}"),
        "focus": target_round.get("focus", ""),
        "speeches": speeches,
        "referee": target_round.get("referee_evaluation", {}),
    }

def get_policy_vectors_evolution(session_data: Dict[str, Any]) -> pd.DataFrame:
    """Extrae la evolución temporal de los 10 parámetros para cada agente y ronda."""
    rows = []
    rounds = session_data.get("rounds", [])
    
    # Agregar estado inicial ronda 0
    initial_map = {
        "capitalist": CAPITALIST_INITIAL_VECTOR.to_dict(),
        "collectivist": COLLECTIVIST_INITIAL_VECTOR.to_dict(),
        "socdem": SOCDEM_INITIAL_VECTOR.to_dict(),
    }
    for agent_id, v_dict in initial_map.items():
        row = {"round": 0, "agent": agent_id, "agent_name": SYSTEM_LABELS.get(agent_id, agent_id)}
        row.update(v_dict)
        rows.append(row)
        
    for r in rounds:
        r_num = r.get("round_number", 0)
        for speech in r.get("speeches", []):
            agent_id = speech.get("agent", "")
            v_dict = speech.get("current_vector", {})
            if v_dict:
                row = {"round": r_num, "agent": agent_id, "agent_name": SYSTEM_LABELS.get(agent_id, agent_id)}
                row.update(v_dict)
                rows.append(row)
                
    # Agregar punto de consenso si existe
    synthesis = session_data.get("synthesis", {})
    if synthesis and "consensus_vector" in synthesis:
        c_vec = synthesis["consensus_vector"]
        row = {"round": len(rounds) + 1, "agent": "consensus", "agent_name": "Consenso Final"}
        row.update(c_vec)
        rows.append(row)
        
    df = pd.DataFrame(rows)
    return df

def compute_pca_trajectory(session_data: Dict[str, Any]) -> Tuple[pd.DataFrame, float, float]:
    """Calcula la proyección PCA 2D de las trayectorias de políticas de los agentes."""
    df_evol = get_policy_vectors_evolution(session_data)
    if df_evol.empty:
        return pd.DataFrame(), 0.0, 0.0
        
    feature_cols = [col for col in POLICY_DIMENSIONS if col in df_evol.columns]
    X = df_evol[feature_cols].values
    
    if len(X) < 2:
        df_evol["pca_x"] = 0.0
        df_evol["pca_y"] = 0.0
        return df_evol, 0.0, 0.0
        
    # Center X
    X_mean = np.mean(X, axis=0)
    X_centered = X - X_mean
    
    # SVD
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    # Principal components
    X_2d = np.dot(X_centered, Vt[:2, :].T)
    
    # Explained variance ratio
    var = (S ** 2) / max(1, len(X) - 1)
    tot_var = np.sum(var) + 1e-9
    var_x = float(var[0] / tot_var * 100.0) if len(var) > 0 else 0.0
    var_y = float(var[1] / tot_var * 100.0) if len(var) > 1 else 0.0
    
    df_evol["pca_x"] = X_2d[:, 0]
    df_evol["pca_y"] = X_2d[:, 1]
    
    return df_evol, var_x, var_y

def compute_convergence_curve(session_data: Dict[str, Any]) -> pd.DataFrame:
    """Calcula la distancia euclídea promedio entre los vectores de los agentes en cada ronda."""
    rounds = session_data.get("rounds", [])
    if not rounds:
        return pd.DataFrame()
        
    records = []
    
    # Ronda 0: distancia inicial
    v_cap = np.array(list(CAPITALIST_INITIAL_VECTOR.to_dict().values()))
    v_col = np.array(list(COLLECTIVIST_INITIAL_VECTOR.to_dict().values()))
    v_soc = np.array(list(SOCDEM_INITIAL_VECTOR.to_dict().values()))
    
    d_init = (np.linalg.norm(v_cap - v_col) + np.linalg.norm(v_cap - v_soc) + np.linalg.norm(v_col - v_soc)) / 3.0
    records.append({"round": 0, "mean_distance": round(float(d_init), 4), "max_distance": round(float(max(np.linalg.norm(v_cap - v_col), np.linalg.norm(v_cap - v_soc))), 4)})
    
    for r in rounds:
        r_num = r.get("round_number", 0)
        vecs = {}
        for speech in r.get("speeches", []):
            agent = speech.get("agent")
            v_dict = speech.get("current_vector", {})
            if v_dict and len(v_dict) == 10:
                vecs[agent] = np.array([v_dict[dim] for dim in POLICY_DIMENSIONS])
                
        if len(vecs) >= 2:
            agent_list = list(vecs.keys())
            dists = []
            for i in range(len(agent_list)):
                for j in range(i + 1, len(agent_list)):
                    dists.append(np.linalg.norm(vecs[agent_list[i]] - vecs[agent_list[j]]))
            mean_d = float(np.mean(dists))
            max_d = float(np.max(dists))
            records.append({"round": r_num, "mean_distance": round(mean_d, 4), "max_distance": round(max_d, 4)})
        else:
            records.append({"round": r_num, "mean_distance": records[-1]["mean_distance"], "max_distance": records[-1]["max_distance"]})
            
    return pd.DataFrame(records)

def extract_concessions_data(session_data: Dict[str, Any]) -> pd.DataFrame:
    """Calcula la magnitud del cambio (concesiones) por parámetro entre inicio y final para cada agente."""
    df_evol = get_policy_vectors_evolution(session_data)
    if df_evol.empty:
        return pd.DataFrame()
        
    records = []
    for agent_id in ["capitalist", "collectivist", "socdem"]:
        df_agent = df_evol[df_evol["agent"] == agent_id].sort_values("round")
        if len(df_agent) >= 2:
            init_row = df_agent.iloc[0]
            final_row = df_agent.iloc[-1]
            for dim in POLICY_DIMENSIONS:
                delta = float(final_row[dim] - init_row[dim])
                records.append({
                    "agent": agent_id,
                    "agent_name": SYSTEM_LABELS.get(agent_id, agent_id),
                    "dimension": dim,
                    "initial_val": round(float(init_row[dim]), 3),
                    "final_val": round(float(final_row[dim]), 3),
                    "delta": round(delta, 3),
                    "abs_delta": round(abs(delta), 3),
                })
                
    return pd.DataFrame(records)

def extract_referee_rubric_history(session_data: Dict[str, Any]) -> pd.DataFrame:
    """Extrae las calificaciones del Árbitro en cada criterio a lo largo de las rondas."""
    rounds = session_data.get("rounds", [])
    records = []
    
    for r in rounds:
        r_num = r.get("round_number", 0)
        ref = r.get("referee_evaluation", {})
        scores = ref.get("rubric_scores", {})
        for agent_id, score_data in scores.items():
            if isinstance(score_data, dict):
                records.append({
                    "round": r_num,
                    "agent": agent_id,
                    "agent_name": SYSTEM_LABELS.get(agent_id, agent_id),
                    "empirical_rigor": score_data.get("empirical_rigor", 7.0),
                    "theoretical_coherence": score_data.get("theoretical_coherence", 8.0),
                    "steelman_score": score_data.get("steelman_score", 7.5),
                    "falsifiability_score": score_data.get("falsifiability_score", 7.0),
                    "total_score": score_data.get("total_score", 7.5),
                })
                
    return pd.DataFrame(records)
