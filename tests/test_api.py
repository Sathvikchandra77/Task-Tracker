import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
import json
from app.main import app

def test_health_ok():
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"

def test_create_and_list_tasks():
    client = app.test_client()
    payload = {"id": "1", "text": "Buy milk"}
    res = client.post("/tasks", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 201
    res = client.get("/tasks")
    assert res.status_code == 200
    items = res.get_json()
    assert any(it["id"] == "1" and it["text"] == "Buy milk" for it in items)
