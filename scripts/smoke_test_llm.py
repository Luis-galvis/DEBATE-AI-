"""
Script de Smoke Test para GroqCloud y Modelos Configurados
Ejecuta llamadas de prueba a los modelos para medir latencia, tokens y verificar la validación Pydantic.
"""

import sys
import time
from pathlib import Path

# Configurar stdout para utf-8 en Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config import (
    is_groq_configured,
    DEBATER_MODEL,
    ARBITER_MODEL,
    FAST_MODEL,
    SECOND_OPINION_MODEL,
)
from src.agents.llm_factory import GroqLLMClient
from src.agents.schemas import PolicyVectorSchema

def run_smoke_test():
    print("=" * 65)
    print("[TEST] INICIANDO SMOKE TEST DE GROQ CLOUD")
    print("=" * 65)

    if not is_groq_configured():
        print("[FAIL] ERROR: GROQ_API_KEY no está configurada en .env.")
        sys.exit(1)

    print("[PASS] Credencial GROQ_API_KEY detectada correctamente (clave protegida).")
    client = GroqLLMClient(mode="live")

    models_to_test = [
        ("FAST_MODEL", FAST_MODEL, 0.2, 100),
        ("DEBATER_MODEL", DEBATER_MODEL, 0.65, 150),
        ("ARBITER_MODEL", ARBITER_MODEL, 0.10, 150),
    ]

    results = []

    for label, model_name, temp, max_tok in models_to_test:
        print(f"\n[REQUEST] Probando {label} [{model_name}]...")
        messages = [
            {"role": "system", "content": "Eres un asistente técnico de economía cuantitativa."},
            {"role": "user", "content": "Define en una sola frase qué es la frontera de posibilidades de producción."}
        ]
        try:
            t0 = time.time()
            text, _, usage = client.call_chat(
                model=model_name,
                messages=messages,
                temperature=temp,
                max_tokens=max_tok
            )
            elapsed_ms = usage.get("latency_ms", (time.time() - t0) * 1000)
            tokens = usage.get("total_tokens", 0)
            print(f"  [OK] Exito | Latencia: {elapsed_ms:.1f}ms | Tokens: {tokens}")
            print(f"  [RESP] {text.strip()[:100]}...")
            results.append((label, model_name, "OK", elapsed_ms, tokens, None))
        except Exception as e:
            print(f"  [FAIL] Fallo en {model_name}: {str(e)}")
            results.append((label, model_name, "ERROR", 0, 0, str(e)))

    # Probar modelo opcional de segunda opinión si está configurado
    if SECOND_OPINION_MODEL:
        print(f"\n[REQUEST] Probando SECOND_OPINION_MODEL (Preview) [{SECOND_OPINION_MODEL}]...")
        messages = [
            {"role": "user", "content": "Di 'OK' en mayúsculas si estás activo."}
        ]
        try:
            t0 = time.time()
            text, _, usage = client.call_chat(
                model=SECOND_OPINION_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=50
            )
            elapsed_ms = usage.get("latency_ms", (time.time() - t0) * 1000)
            print(f"  [OK] Exito Preview | Latencia: {elapsed_ms:.1f}ms | Respuesta: {text.strip()[:60]}")
            results.append(("SECOND_OPINION_MODEL", SECOND_OPINION_MODEL, "OK", elapsed_ms, usage.get("total_tokens", 0), None))
        except Exception as e:
            print(f"  [WARN] Modelo preview no critico no respondio: {str(e)}")
            results.append(("SECOND_OPINION_MODEL", SECOND_OPINION_MODEL, "OPTIONAL_FAIL", 0, 0, str(e)))

    # Probar salida estructurada Pydantic
    print(f"\n[REQUEST] Probando Salida Estructurada JSON (Pydantic PolicyVectorSchema) con {FAST_MODEL}...")
    schema_prompt = [
        {
            "role": "system",
            "content": (
                "Eres un optimizador de políticas macroeconómicas. Responde ÚNICAMENTE un JSON válido que cumpla con el esquema PolicyVectorSchema con valores flotantes entre 0.0 y 1.0 para los 10 campos: state_ownership, max_tax_rate, tax_progressivity, public_spending_gdp, social_transfers_coverage, market_regulation, labor_protection, trade_openness, fiscal_rule_strictness, central_bank_independence."
            )
        },
        {
            "role": "user",
            "content": "Genera el vector de política económica para un modelo nórdico con alta protección social y alta apertura de mercado."
        }
    ]

    try:
        raw_json, parsed_obj, usage = client.call_chat(
            model=FAST_MODEL,
            messages=schema_prompt,
            temperature=0.1,
            max_tokens=400,
            response_model=PolicyVectorSchema
        )
        if isinstance(parsed_obj, PolicyVectorSchema):
            print(f"  [OK] Validacion Pydantic EXITOSA:")
            print(f"     - Gasto publico: {parsed_obj.public_spending_gdp}")
            print(f"     - Apertura comercial: {parsed_obj.trade_openness}")
            print(f"     - Transferencias: {parsed_obj.social_transfers_coverage}")
        else:
            print(f"  [WARN] Parseo Pydantic devolvio tipo: {type(parsed_obj)}")
    except Exception as e:
        print(f"  [FAIL] Error en validacion estructurada Pydantic: {str(e)}")

    print("\n" + "=" * 65)
    print("RESUMEN DEL SMOKE TEST")
    print("=" * 65)
    for label, model_name, status, lat, toks, err in results:
        status_tag = "[OK]  " if status == "OK" else ("[WARN]" if status == "OPTIONAL_FAIL" else "[FAIL]")
        print(f"{status_tag} {label:<22} | {model_name:<28} | {lat:>6.1f} ms | {toks:>4} tok")

    print("=" * 65)

if __name__ == "__main__":
    run_smoke_test()
