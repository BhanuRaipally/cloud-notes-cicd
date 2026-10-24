import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app

def test_homepage_returns_200():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"DevOps Status Dashboard" in response.data

def test_health_endpoint_returns_ok():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert "version" in payload

def test_version_can_be_displayed():
    client = app.test_client()
    response = client.get("/")
    assert b"Deployment version" in response.data
