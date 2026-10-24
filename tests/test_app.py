import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app

def test_homepage():
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b"Cloud Notes" in response.data

def test_health_endpoint():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_version_is_visible():
    response = app.test_client().get("/")
    assert b"Version:" in response.data
