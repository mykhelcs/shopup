import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.dependencies.auth_dependency import get_current_user
from app.database.connection import get_db
from app.models.all_models import User, UserRole

# Mock user
mock_user = User(
    id=1,
    firebase_uid="test_uid",
    email="test@example.com",
    role=UserRole.CUSTOMER,
    full_name="Original Name",
    address="Original Address",
    phone_number="1234567890",
    created_at=datetime.now(timezone.utc)
)

async def mock_get_current_user():
    return mock_user

async def mock_get_db():
    session = AsyncMock()
    # Mock refresh to update object if needed, or just pass
    session.refresh = AsyncMock()
    yield session

app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_db] = mock_get_db

@pytest.mark.anyio
async def test_get_user_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Original Name"

@pytest.mark.anyio
async def test_update_user_profile():
    new_data = {
        "full_name": "Updated Name",
        "address": "Updated Address",
        "phone_number": "0987654321"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put("/users/me", json=new_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["address"] == "Updated Address"
    assert data["phone_number"] == "0987654321"
    
    # Verify mock user updated (in-memory specific check, might flaky if DB not mocked correctly but good for unit test of route logic)
    assert mock_user.full_name == "Updated Name"
