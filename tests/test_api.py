from autogenesis_agent.api import create_app
from autogenesis_agent.storage import connect


def test_local_api_chat_endpoint_returns_output(tmp_path):
    from fastapi.testclient import TestClient

    db = connect(tmp_path / "agent.sqlite")
    app = create_app(db)
    client = TestClient(app)

    response = client.post("/sessions", json={"user_id": "user-1", "channel": "api", "workspace": str(tmp_path)})
    assert response.status_code == 200
    session_id = response.json()["id"]

    response = client.post(f"/sessions/{session_id}/chat", json={"message": "hello api"})

    assert response.status_code == 200
    assert response.json()["output"] == "hello api"
    assert response.json()["trace_id"].startswith("trc_")
