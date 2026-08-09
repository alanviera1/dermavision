from fastapi.testclient import TestClient

from dermavision.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_pending() -> None:
    response = client.post("/api/v1/analyze")
    assert response.status_code == 501
