
from google import genai
from google.genai import types

from backend.app.core.config import settings
from backend.app.agents.prompts import SYSTEM_INSTRUCTION

def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options=types.HttpOptions(
            timeout=30000
        )
    )


def generate_response(user_message: str) -> str:
    """
    Send a message to Gemini and return its response.
    """

    client = get_gemini_client()

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2
        )
    )

    return response.text or "I could not generate a response."
