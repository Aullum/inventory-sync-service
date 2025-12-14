import httpx
from fastapi.testclient import TestClient

from main import app


def test_lifespan_smoke_initializes_and_closes_http_client(monkeypatch):
    monkeypatch.setenv("EBAY_CLIENT_ID", "test-ebay-client-id")
    monkeypatch.setenv("EBAY_CLIENT_SECRET", "test-ebay-client-secret")

    with TestClient(app):
        assert hasattr(app.state, "config")
        assert hasattr(app.state, "http")
        assert isinstance(app.state.http, httpx.AsyncClient)
