import os
import logging
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:1b",
)

OLLAMA_TIMEOUT = float(
    os.getenv("OLLAMA_TIMEOUT", "60")
)


def is_ollama_available() -> bool:
    """Return True when the local Ollama server is reachable."""
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=5,
        )
        return response.ok
    except requests.RequestException as exc:
        logger.info("Ollama unavailable: %s", exc)
        return False


def generate(
    prompt: str,
    *,
    model: Optional[str] = None,
    timeout: Optional[float] = None,
) -> Optional[str]:
    """
    Generate text using the local Ollama server.

    Returns:
        Generated text when successful.
        None when Ollama is unavailable or generation fails.
    """
    if not prompt.strip():
        return None

    selected_model = model or OLLAMA_MODEL
    selected_timeout = timeout or OLLAMA_TIMEOUT

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=selected_timeout,
        )
        response.raise_for_status()

        data = response.json()
        result = data.get("response")

        if not isinstance(result, str):
            logger.warning("Ollama response did not contain text")
            return None

        return result.strip() or None

    except (requests.RequestException, ValueError) as exc:
        logger.warning("Ollama generation failed: %s", exc)
        return None
