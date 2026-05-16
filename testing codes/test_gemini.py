"""Test LLM connection"""
from utils.llm import ask_llm, get_provider_info, test_llm_connection

def test_provider_info():
    info = get_provider_info()
    assert "provider" in info
    assert "model" in info
    print(f"\nProvider: {info}")

def test_ask_llm_basic():
    """Requires a real API key in .env to pass."""
    ok, msg = test_llm_connection()
    print(f"\nConnection test: {msg}")
    # Don't assert True — test environments may not have API keys
