"""
Integration tests for Bloomberg Terminal FastAPI Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "Bloomberg" in data["name"]


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analysis_stock_offline_fallback():
    """Tests that AI analysis endpoint works reliably even without external Gemini keys"""
    response = client.get("/api/analysis/stock/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "analysis" in data
    assert len(data["analysis"]) > 50


def test_chat_offline_fallback():
    response = client.post("/api/analysis/chat", json={"message": "What is the P/E ratio?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
