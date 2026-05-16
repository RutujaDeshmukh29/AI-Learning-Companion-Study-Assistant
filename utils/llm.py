"""
LLM Module — Provider-agnostic language model interface
========================================================
Supports: Groq (default), OpenAI-compatible APIs
Swap provider by changing LLM_PROVIDER in .env

WHY this design:
- Your original llm.py was hardcoded to Groq.
- If you ever want to switch to Gemini/OpenAI, you'd rewrite everything.
- This wrapper lets you swap providers via a single .env variable.
- All other modules (rag_pipeline, quiz_generator, etc.) just call ask_llm()
  and never need to know which provider is running underneath.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Provider selection ──────────────────────────────────────────────────────
# Set LLM_PROVIDER in your .env: "groq" | "openai" | "gemini"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# ── Model defaults per provider ─────────────────────────────────────────────
DEFAULT_MODELS = {
    "groq":   "llama-3.1-8b-instant",
    "openai": "gpt-3.5-turbo",
    "gemini": "gemini-1.5-flash",
}

# ── Singleton clients (lazy-initialized) ────────────────────────────────────
_groq_client   = None
_openai_client = None
_gemini_model  = None


# ── Internal: initialize Groq ───────────────────────────────────────────────
def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not set in .env")
            _groq_client = Groq(api_key=api_key)
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")
    return _groq_client


# ── Internal: initialize OpenAI ─────────────────────────────────────────────
def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in .env")
            _openai_client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    return _openai_client


# ── Internal: initialize Gemini ─────────────────────────────────────────────
def _get_gemini_model():
    global _gemini_model
    if _gemini_model is None:
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set in .env")
            genai.configure(api_key=api_key)
            _gemini_model = genai.GenerativeModel(
                model_name=os.getenv("LLM_MODEL", DEFAULT_MODELS["gemini"]),
                generation_config={"temperature": 0.7, "max_output_tokens": 2048}
            )
        except ImportError:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
    return _gemini_model


# ── Public: ask_llm ──────────────────────────────────────────────────────────
def ask_llm(prompt: str, system_prompt: str = None) -> str:
    """
    Send a prompt to the configured LLM and return the response text.

    Args:
        prompt:        The user/task prompt.
        system_prompt: Optional system-level instruction (ignored for Gemini basic).

    Returns:
        Generated response as a string.
    """
    provider = LLM_PROVIDER

    try:
        if provider == "groq":
            return _ask_groq(prompt, system_prompt)
        elif provider == "openai":
            return _ask_openai(prompt, system_prompt)
        elif provider == "gemini":
            return _ask_gemini(prompt)
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'. Use 'groq', 'openai', or 'gemini'.")

    except Exception as e:
        error = str(e)
        if "quota" in error.lower() or "rate" in error.lower():
            return "⚠️ API rate limit hit. Please wait a moment and try again."
        if "api key" in error.lower() or "authentication" in error.lower():
            return "⚠️ Invalid API key. Check your .env file."
        if "model" in error.lower():
            return f"⚠️ Model error: {error}"
        return f"⚠️ LLM error: {error}"


def _ask_groq(prompt: str, system_prompt: str = None) -> str:
    client = _get_groq_client()
    model  = os.getenv("LLM_MODEL", DEFAULT_MODELS["groq"])

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
    )
    return response.choices[0].message.content


def _ask_openai(prompt: str, system_prompt: str = None) -> str:
    client = _get_openai_client()
    model  = os.getenv("LLM_MODEL", DEFAULT_MODELS["openai"])

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
    )
    return response.choices[0].message.content


def _ask_gemini(prompt: str) -> str:
    model    = _get_gemini_model()
    response = model.generate_content(prompt)
    return response.text


# ── Public: get_provider_info ────────────────────────────────────────────────
def get_provider_info() -> dict:
    """Return current LLM provider config (useful for UI display)."""
    return {
        "provider": LLM_PROVIDER,
        "model":    os.getenv("LLM_MODEL", DEFAULT_MODELS.get(LLM_PROVIDER, "unknown")),
    }


# ── Public: test_connection ──────────────────────────────────────────────────
def test_llm_connection() -> tuple[bool, str]:
    """
    Quick connectivity test. Returns (success, message).
    Called from the UI sidebar to validate API key on startup.
    """
    try:
        response = ask_llm("Reply with exactly: OK")
        if "⚠️" in response:
            return False, response
        return True, f"✅ {LLM_PROVIDER.capitalize()} connected — model ready"
    except Exception as e:
        return False, f"❌ Connection failed: {str(e)}"
