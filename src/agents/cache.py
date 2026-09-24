"""
Módulo de Caché para Grabar y Reproducir llamadas a LLM (Record & Replay).
Permite garantizar reproducibilidad exacta y cero costos adicionales al repetir debates.
"""

import sqlite3
import json
import hashlib
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from src.config import CACHE_DB_PATH, OUTPUTS_DIR

class LLMCache:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or CACHE_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS llm_cache (
                    cache_key TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    prompt_preview TEXT,
                    response_content TEXT NOT NULL,
                    usage_json TEXT,
                    latency_ms REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def generate_key(model: str, messages: list, params: Dict[str, Any]) -> str:
        """Genera un hash SHA256 determinista a partir de los inputs de la llamada."""
        serialized = {
            "model": model,
            "messages": messages,
            "params": {k: v for k, v in params.items() if k not in ("api_key", "timeout")}
        }
        raw_str = json.dumps(serialized, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Recupera una respuesta en caché si existe."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT model, response_content, usage_json, latency_ms FROM llm_cache WHERE cache_key = ?",
                (cache_key,)
            )
            row = cursor.fetchone()
            if row:
                model, content, usage_json, latency_ms = row
                return {
                    "model": model,
                    "content": content,
                    "usage": json.loads(usage_json) if usage_json else {},
                    "latency_ms": latency_ms,
                    "cached": True
                }
        return None

    def set(
        self,
        cache_key: str,
        model: str,
        messages: list,
        response_content: str,
        usage: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0
    ):
        """Guarda una respuesta en la caché."""
        prompt_preview = json.dumps(messages[-1] if messages else {}, ensure_ascii=False)[:300]
        usage_json = json.dumps(usage or {})
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO llm_cache (cache_key, model, prompt_preview, response_content, usage_json, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cache_key, model, prompt_preview, response_content, usage_json, latency_ms)
            )
            conn.commit()

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM llm_cache")
            return cursor.fetchone()[0]
