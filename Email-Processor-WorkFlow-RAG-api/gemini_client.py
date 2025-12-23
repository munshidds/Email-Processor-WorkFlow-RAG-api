from typing import Optional

import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None  # type: ignore

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None  # type: ignore


class GeminiNotConfigured(Exception):
    pass


def _get_client():
    if load_dotenv is not None:
        load_dotenv()  # load from .env if present

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiNotConfigured("GEMINI_API_KEY environment variable is not set.")
    if genai is None:
        raise GeminiNotConfigured(
            "google-generativeai package is not installed. "
            "Install it with `pip install google-generativeai`."
        )
    genai.configure(api_key=api_key)
    return genai


def explain_order_status(rag_context: str, user_query: str) -> Optional[str]:
    """
    Use Gemini to generate a natural language explanation of the order status using
    retrieved context (RAG-style).

    This is optional and will only work if GEMINI_API_KEY is set and
    google-generativeai is installed. Otherwise it returns None.
    """
    try:
        client = _get_client()
    except GeminiNotConfigured as e:
        print(f"[gemini] not configured: {e}", file=sys.stderr)
        return None
    except Exception as e:  # pragma: no cover
        print(f"[gemini] unexpected config error: {e}", file=sys.stderr)
        return None

    prompt = (
        "You are an order-tracking assistant. Use ONLY the provided context to answer. "
        "Do not fabricate details that are not in the context.\n\n"
        "CONTEXT:\n"
        f"{rag_context}\n\n"
        "USER QUERY:\n"
        f"{user_query}\n\n"
        "Instructions:\n"
        "- If the order is present, give status and brief next step in 2-3 sentences.\n"
        "- If uncertain, say you don't have enough info from the context.\n"
    )

    model = client.GenerativeModel("gemini-2.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text if hasattr(response, "text") else None
    except Exception as e:  # pragma: no cover
        print(f"[gemini] generation failed: {e}", file=sys.stderr)
        return None



