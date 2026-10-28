import pytest
from sqlalchemy.pool import StaticPool
from app import create_app
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool
    }
    OLLAMA_BASE_URL = "http://localhost:11434"

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] in ("online", "degraded")
    assert "database" in data

def test_llm_status_endpoint(client):
    res = client.get("/api/llm/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["provider"] == "ollama"
    assert "is_reachable" in data

def test_conversation_lifecycle(client):
    headers = {"X-Session-Id": "test-session-123"}

    # 1. Create conversation
    res = client.post("/api/conversations", json={"title": "Admissions Inquiry"}, headers=headers)
    assert res.status_code == 201
    conv = res.get_json()
    conv_id = conv["id"]
    assert conv["title"] == "Admissions Inquiry"

    # 2. List conversations
    res_list = client.get("/api/conversations", headers=headers)
    assert res_list.status_code == 200
    assert res_list.get_json()["count"] >= 1

    # 3. Patch conversation title
    res_patch = client.patch(f"/api/conversations/{conv_id}", json={"title": "Updated Title"}, headers=headers)
    assert res_patch.status_code == 200
    assert res_patch.get_json()["title"] == "Updated Title"

    # 4. Delete conversation
    res_del = client.delete(f"/api/conversations/{conv_id}", headers=headers)
    assert res_del.status_code == 200

def test_chat_rule_match(client):
    headers = {"X-Session-Id": "chat-session-456"}
    res = client.post("/api/chat", json={"message": "Hello!"}, headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["response_type"] == "rule"
    assert "KBN University" in data["message"]["content"]
