from typing import Optional

import os

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None  # type: ignore


class GeminiNotConfigured(Exception):
    pass


def _get_client():
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


def explain_order_status(order_summary: str, user_query: str) -> Optional[str]:
    """
    Use Gemini to generate a natural language explanation of the order status.

    This is optional and will only work if GEMINI_API_KEY is set and
    google-generativeai is installed. Otherwise it returns None.
    """
    try:
        client = _get_client()
    except GeminiNotConfigured:
        return None

    prompt = (
        "You are an order-tracking assistant. Based on the following order summary "
        "and user query, answer briefly with the current status of the order and any "
        "useful next steps.\n\n"
        f"ORDER SUMMARY:\n{order_summary}\n\n"
        f"USER QUERY:\n{user_query}\n\n"
        "Answer in 2-3 short sentences."
    )

    model = client.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else None


