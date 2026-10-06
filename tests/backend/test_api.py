import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
backend_dir = repo_root / 'backend'
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_build_endpoint_returns_valid_response():
    payload = {
        'prompt': 'Create a modern fintech landing page',
        'tone': 'premium',
        'style': 'dark',
    }

    response = client.post('/api/build', json=payload)
    assert response.status_code == 200
    body = response.json()
    assert 'title' in body
    assert 'app_type' in body
    assert 'pages' in body
    assert 'sections' in body
    assert 'hero_headline' in body
    assert 'hero_text' in body


def test_invalid_build_request():
    response = client.post('/api/build', json={'prompt': 'x'})
    assert response.status_code == 400


def test_response_structure_for_portfolio_prompt():
    payload = {
        'prompt': 'Build a portfolio site for a photographer in Lagos',
        'tone': 'creative',
        'style': 'light',
    }

    response = client.post('/api/build', json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body['app_type'] == 'portfolio'
    assert body['theme'] == 'creative light'
    assert isinstance(body['pages'], list)
    assert isinstance(body['sections'], list)
