import sys
from pathlib import Path
from unittest.mock import patch

repo_root = Path(__file__).resolve().parents[2]
backend_dir = repo_root / 'backend'
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    """Test that the health endpoint returns a healthy response."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert 'message' in data


def test_build_endpoint_returns_valid_response():
    """Test that /api/build returns a valid app spec without external API calls."""
    payload = {
        'prompt': 'Create a modern fintech landing page',
        'tone': 'premium',
        'style': 'dark',
    }

    response = client.post('/api/build', json=payload)
    assert response.status_code == 200
    data = response.json()

    assert 'title' in data
    assert 'app_type' in data
    assert 'theme' in data
    assert 'style' in data
    assert 'pages' in data
    assert 'sections' in data
    assert 'hero_headline' in data
    assert 'hero_text' in data

    assert isinstance(data['pages'], list)
    assert len(data['pages']) > 0
    assert isinstance(data['sections'], list)
    assert len(data['sections']) > 0


def test_invalid_build_request_too_short():
    """Test that a prompt that is too short returns a 400 error."""
    response = client.post('/api/build', json={'prompt': 'x'})
    assert response.status_code == 400
    assert 'detail' in response.json()


def test_invalid_build_request_missing_prompt():
    """Test that a missing prompt returns a validation error."""
    response = client.post('/api/build', json={})
    assert response.status_code == 422


def test_response_structure_for_portfolio_prompt():
    """Test that portfolio prompts are correctly classified without external calls."""
    payload = {
        'prompt': 'Build a portfolio site for a photographer',
        'tone': 'creative',
        'style': 'light',
    }

    response = client.post('/api/build', json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data['app_type'] == 'portfolio'
    assert data['theme'] == 'creative light'
    assert isinstance(data['pages'], list)
    assert isinstance(data['sections'], list)
    assert 'gallery' in data['pages']


def test_response_structure_for_dashboard_prompt():
    """Test that dashboard prompts are correctly classified without external calls."""
    payload = {
        'prompt': 'Create an analytics dashboard with charts and metrics',
        'tone': 'modern',
        'style': 'dark',
    }

    response = client.post('/api/build', json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data['app_type'] == 'dashboard'
    assert isinstance(data['pages'], list)
    assert 'analytics' in data['pages']


@patch('main.get_weather')
@patch('main.get_city_data')
def test_city_enrichment_with_mocked_apis(mock_city_data, mock_weather):
    """Test that city/weather enrichment works with mocked external API calls."""
    mock_city_data.return_value = {
        'city': 'Lagos',
        'lat': 6.5244,
        'lon': 3.3792,
        'display_name': 'Lagos, Nigeria',
    }
    mock_weather.return_value = '28°C'

    payload = {
        'prompt': 'Build a portfolio site for a photographer in Lagos',
        'tone': 'creative',
        'style': 'light',
    }

    response = client.post('/api/build', json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data['location'] is not None
    assert data['location']['city'] == 'Lagos'
    assert data['location']['weather'] == '28°C'
    assert mock_city_data.called
    assert mock_weather.called


@patch('main.get_weather')
@patch('main.get_city_data')
def test_city_enrichment_fallback_on_api_failure(mock_city_data, mock_weather):
    """Test that graceful fallback behavior works when external APIs fail."""
    mock_city_data.return_value = {'city': 'UnknownCity'}
    mock_weather.return_value = 'N/A'

    payload = {
        'prompt': 'Build a site for a startup in Tokyo',
        'tone': 'modern',
        'style': 'dark',
    }

    response = client.post('/api/build', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 'title' in data
    assert 'app_type' in data


def test_templates_endpoint():
    """Test that the templates list endpoint works."""
    response = client.get('/api/templates')
    assert response.status_code == 200
    data = response.json()

    assert 'templates' in data
    assert isinstance(data['templates'], list)
    assert len(data['templates']) > 0

    for template in data['templates']:
        assert 'id' in template
        assert 'name' in template
        assert 'description' in template


def test_root_endpoint():
    """Test that the root endpoint returns API metadata."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()

    assert 'name' in data
    assert 'version' in data
    assert 'docs' in data
    assert 'api' in data
