"""API Tests."""
from fastapi.testclient import TestClient
from api.app import app
client = TestClient(app)

def test_health(): assert client.get("/health").status_code == 200
# Route tests
