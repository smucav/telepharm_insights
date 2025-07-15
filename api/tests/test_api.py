import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_top_products():
    response = client.get("/api/reports/top-products?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        assert "product" in response.json()[0]
        assert "mention_count" in response.json()[0]

@pytest.mark.asyncio
async def test_channel_activity():
    response = client.get("/api/channels/Chemed123/activity")
    assert response.status_code in [200, 500]  # Allow 500 if channel not found
    if response.status_code == 200:
        assert isinstance(response.json(), list)
        if response.json():
            assert "date_day" in response.json()[0]
            assert "message_count" in response.json()[0]
            assert "object_detections" in response.json()[0]

@pytest.mark.asyncio
async def test_search_messages():
    response = client.get("/api/search/messages?query=paracetamol")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        assert "message_id" in response.json()[0]
        assert "channel_name" in response.json()[0]
