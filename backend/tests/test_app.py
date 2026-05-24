import io
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.config import get_settings


def test_healthcheck():
    settings = get_settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_planner_preview_route():
    with TestClient(app) as client:
        response = client.post("/planner/preview", json={"kind": "checklist", "objective": "Testing, Release"})

    assert response.status_code == 200
    assert response.json()["data"]["kind"] == "checklist"


def test_ingest_manual_dataset_route():
    with TestClient(app) as client:
        response = client.post(
            "/ingest/data",
            data={
                "dataset_name": "Manual Data",
                "kind": "csv",
                "content": "day,value\nMon,10\nTue,20",
            },
        )

    payload = response.json()["data"]
    assert response.status_code == 200
    assert payload["summary"]["row_count"] == 2


def test_qr_generate_route():
    with TestClient(app) as client:
        response = client.post("/qr", data={"mode": "generate", "payload_text": "https://example.com"})

    payload = response.json()["data"]
    assert response.status_code == 200
    assert payload["image_base64"]


def test_home_assistant_status_route_without_config():
    with TestClient(app) as client:
        response = client.get("/integrations/home-assistant/status")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "not_configured"


def test_vision_analyze_route():
    image = Image.new("RGB", (48, 32), color=(10, 200, 120))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    with TestClient(app) as client:
        response = client.post(
            "/vision/analyze",
            files={"file": ("sample.png", buffer.getvalue(), "image/png")},
        )

    payload = response.json()["data"]
    assert response.status_code == 200
    assert payload["width"] == 48
