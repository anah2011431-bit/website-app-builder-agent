import sys
from pathlib import Path
from unittest.mock import patch

repo_root = Path(__file__).resolve().parents[2]
backend_dir = repo_root / "backend"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app
from fastapi.testclient import TestClient


client = TestClient(app)


FALLBACK_SPEC = {
    "title": "Test App",
    "app_type": "landing-page",
    "theme": "premium dark",
    "style": "dark",
    "pages": ["home", "features"],
    "sections": ["hero", "cta"],
    "hero_headline": "Test Headline",
    "hero_text": "Test application.",
}


def test_health_check():
    """Test that the health endpoint returns a healthy response."""
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "message" in data


@patch("main.generate_ai_app_spec")
def test_build_endpoint_returns_valid_response(mock_generate):
    """Test /api/build without depending on Ollama."""
    mock_generate.return_value = (
        FALLBACK_SPEC,
        "fallback",
    )

    payload = {
        "prompt": "Create a modern fintech landing page",
        "tone": "premium",
        "style": "dark",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "title" in data
    assert "app_type" in data
    assert "theme" in data
    assert "style" in data
    assert "pages" in data
    assert "sections" in data
    assert "hero_headline" in data
    assert "hero_text" in data

    assert isinstance(data["pages"], list)
    assert len(data["pages"]) > 0

    assert isinstance(data["sections"], list)
    assert len(data["sections"]) > 0

    mock_generate.assert_called_once()


def test_invalid_build_request_too_short():
    """Test that a prompt that is too short returns a 400 error."""
    response = client.post(
        "/api/build",
        json={"prompt": "x"},
    )

    assert response.status_code == 400
    assert "detail" in response.json()


def test_invalid_build_request_missing_prompt():
    """Test that a missing prompt returns a validation error."""
    response = client.post(
        "/api/build",
        json={},
    )

    assert response.status_code == 422


@patch("main.generate_ai_app_spec")
def test_response_structure_for_portfolio_prompt(mock_generate):
    """Test portfolio classification without calling Ollama."""
    mock_generate.return_value = (
        {
            **FALLBACK_SPEC,
            "app_type": "portfolio",
            "theme": "creative light",
            "pages": [
                "home",
                "gallery",
                "about",
                "contact",
            ],
        },
        "fallback",
    )

    payload = {
        "prompt": "Build a portfolio site for a photographer",
        "tone": "creative",
        "style": "light",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["app_type"] == "portfolio"
    assert data["theme"] == "creative light"
    assert isinstance(data["pages"], list)
    assert isinstance(data["sections"], list)
    assert "gallery" in data["pages"]


@patch("main.generate_ai_app_spec")
def test_response_structure_for_dashboard_prompt(mock_generate):
    """Test dashboard classification without calling Ollama."""
    mock_generate.return_value = (
        {
            **FALLBACK_SPEC,
            "app_type": "dashboard",
            "pages": [
                "overview",
                "analytics",
                "settings",
            ],
        },
        "fallback",
    )

    payload = {
        "prompt": "Create an analytics dashboard with charts and metrics",
        "tone": "modern",
        "style": "dark",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["app_type"] == "dashboard"
    assert isinstance(data["pages"], list)
    assert "analytics" in data["pages"]


@patch("main.get_weather")
@patch("main.get_city_data")
@patch("main.generate_ai_app_spec")
def test_city_enrichment_with_mocked_apis(
    mock_generate,
    mock_city_data,
    mock_weather,
):
    """Test city/weather enrichment with mocked external APIs."""
    mock_generate.return_value = (
        {
            **FALLBACK_SPEC,
            "app_type": "portfolio",
        },
        "fallback",
    )

    mock_city_data.return_value = {
        "city": "Lagos",
        "lat": 6.5244,
        "lon": 3.3792,
        "display_name": "Lagos, Nigeria",
    }

    mock_weather.return_value = "28°C"

    payload = {
        "prompt": "Build a portfolio site for a photographer in Lagos",
        "tone": "creative",
        "style": "light",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["location"] is not None
    assert data["location"]["city"] == "Lagos"
    assert data["location"]["weather"] == "28°C"

    assert mock_city_data.called
    assert mock_weather.called


@patch("main.get_weather")
@patch("main.get_city_data")
@patch("main.generate_ai_app_spec")
def test_city_enrichment_fallback_on_api_failure(
    mock_generate,
    mock_city_data,
    mock_weather,
):
    """Test graceful behavior when external APIs fail."""
    mock_generate.return_value = (
        FALLBACK_SPEC,
        "fallback",
    )

    mock_city_data.return_value = {
        "city": "UnknownCity"
    }

    mock_weather.return_value = "N/A"

    payload = {
        "prompt": "Build a site for a startup in Tokyo",
        "tone": "modern",
        "style": "dark",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "title" in data
    assert "app_type" in data


def test_templates_endpoint():
    """Test that the templates list endpoint works."""
    response = client.get("/api/templates")

    assert response.status_code == 200

    data = response.json()

    assert "templates" in data
    assert isinstance(data["templates"], list)
    assert len(data["templates"]) > 0

    for template in data["templates"]:
        assert "id" in template
        assert "name" in template
        assert "description" in template


def test_root_endpoint():
    """Test that the root endpoint returns API metadata."""
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert "api" in data


# ---------------------------------------------------------------------------
# Phase 2 — Ollama integration tests
# ---------------------------------------------------------------------------


@patch("main.ollama_generate")
@patch("main.is_ollama_available")
def test_ollama_valid_appspec(
    mock_available,
    mock_generate,
):
    """Test that a valid Ollama AppSpec is accepted."""
    mock_available.return_value = True

    mock_generate.return_value = """
    {
        "title": "Fintech Landing Page",
        "app_type": "landing-page",
        "theme": "premium dark",
        "style": "dark",
        "pages": ["home", "features", "pricing"],
        "sections": ["hero", "features", "cta"],
        "hero_headline": "Finance Made Simple",
        "hero_text": "Modern financial tools for growing businesses."
    }
    """

    payload = {
        "prompt": "Create a fintech landing page",
        "tone": "premium",
        "style": "dark",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Fintech Landing Page"
    assert data["app_type"] == "landing-page"
    assert data["hero_headline"] == "Finance Made Simple"

    mock_available.assert_called_once()
    mock_generate.assert_called_once()


@patch("main.is_ollama_available")
def test_ollama_unavailable_uses_fallback(mock_available):
    """Test deterministic fallback when Ollama is unavailable."""
    mock_available.return_value = False

    payload = {
        "prompt": "Create an analytics dashboard",
        "tone": "modern",
        "style": "dark",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["app_type"] == "dashboard"
    assert data["title"] == "Analytics Dashboard"


@patch("main.ollama_generate")
@patch("main.is_ollama_available")
def test_malformed_ollama_response_uses_fallback(
    mock_available,
    mock_generate,
):
    """Test fallback when Ollama returns malformed JSON."""
    mock_available.return_value = True

    mock_generate.return_value = """
    THIS IS NOT VALID JSON
    """

    payload = {
        "prompt": "Create an ecommerce store",
        "tone": "modern",
        "style": "light",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["app_type"] == "ecommerce"
    assert data["title"] == "Online Store"


@patch("main.ollama_generate")
@patch("main.is_ollama_available")
def test_ollama_invalid_schema_uses_fallback(
    mock_available,
    mock_generate,
):
    """Test fallback when Ollama returns invalid AppSpec schema."""
    mock_available.return_value = True

    mock_generate.return_value = """
    {
        "title": "Broken AppSpec",
        "app_type": "invalid-type",
        "theme": "dark",
        "style": "dark",
        "pages": ["home"],
        "sections": ["hero"],
        "hero_headline": "Broken",
        "hero_text": "Invalid application type."
    }
    """

    payload = {
        "prompt": "Create a portfolio website",
        "tone": "creative",
        "style": "dark",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["app_type"] == "portfolio"
    assert data["title"] == "Creative Portfolio"


@patch("main.ollama_generate")
@patch("main.is_ollama_available")
def test_unknown_request_remains_safe(
    mock_available,
    mock_generate,
):
    """Test that an unknown request produces a valid safe AppSpec."""
    mock_available.return_value = True

    mock_generate.return_value = """
    {
        "title": "Safe General Website",
        "app_type": "landing-page",
        "theme": "modern light",
        "style": "light",
        "pages": ["home"],
        "sections": ["hero"],
        "hero_headline": "Welcome",
        "hero_text": "A simple starting point."
    }
    """

    payload = {
        "prompt": "Build something useful for my business",
        "tone": "modern",
        "style": "light",
    }

    response = client.post(
        "/api/build",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["app_type"] == "landing-page"
    assert data["pages"]
    assert data["sections"]
