import json
from typing import Any, Optional


ALLOWED_APP_TYPES = {
    "landing-page",
    "dashboard",
    "portfolio",
    "ecommerce",
    "blog",
    "app",
}

REQUIRED_FIELDS = {
    "title",
    "app_type",
    "theme",
    "style",
    "pages",
    "sections",
    "hero_headline",
    "hero_text",
}


def parse_appspec(raw_output: str) -> Optional[dict[str, Any]]:
    """
    Parse and validate an Ollama AppSpec response.

    Returns a normalized AppSpec dictionary when valid.
    Returns None when the AI response is malformed or unsafe to use.
    """
    if not isinstance(raw_output, str) or not raw_output.strip():
        return None

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    if not REQUIRED_FIELDS.issubset(data.keys()):
        return None

    app_type = data.get("app_type")

    if app_type not in ALLOWED_APP_TYPES:
        return None

    string_fields = [
        "title",
        "app_type",
        "theme",
        "style",
        "hero_headline",
        "hero_text",
    ]

    for field in string_fields:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            return None

    for field in ["pages", "sections"]:
        value = data.get(field)

        if not isinstance(value, list):
            return None

        if not all(isinstance(item, str) and item.strip() for item in value):
            return None

    return {
        "title": data["title"].strip(),
        "app_type": data["app_type"].strip(),
        "theme": data["theme"].strip(),
        "style": data["style"].strip(),
        "pages": [item.strip() for item in data["pages"]],
        "sections": [item.strip() for item in data["sections"]],
        "hero_headline": data["hero_headline"].strip(),
        "hero_text": data["hero_text"].strip(),
    }
