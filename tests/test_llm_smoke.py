"""
Tests unitarios para verificar la fábrica de LLM, caché y validación de esquemas.
"""

import pytest
from src.config import is_groq_configured, FAST_MODEL
from src.agents.llm_factory import GroqLLMClient
from src.agents.cache import LLMCache
from src.agents.schemas import PolicyVectorSchema, RefereeTurnEvaluation

def test_groq_api_key_configured():
    assert is_groq_configured() is True

def test_cache_key_generation():
    messages = [{"role": "user", "content": "Hola"}]
    params = {"temperature": 0.5, "max_tokens": 100}
    key1 = LLMCache.generate_key("model-a", messages, params)
    key2 = LLMCache.generate_key("model-a", messages, params)
    key3 = LLMCache.generate_key("model-b", messages, params)
    assert key1 == key2
    assert key1 != key3

def test_policy_vector_schema_validation():
    valid_data = {
        "state_ownership": 0.15,
        "max_tax_rate": 0.35,
        "tax_progressivity": 0.50,
        "public_spending_gdp": 0.25,
        "social_transfers_coverage": 0.30,
        "market_regulation": 0.40,
        "labor_protection": 0.35,
        "trade_openness": 0.80,
        "fiscal_rule_strictness": 0.75,
        "central_bank_independence": 0.90
    }
    vec = PolicyVectorSchema(**valid_data)
    assert len(vec.to_array()) == 10
    assert vec.trade_openness == 0.80

    # Bounds check
    with pytest.raises(Exception):
        PolicyVectorSchema(state_ownership=1.5)
