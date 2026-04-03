import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.db.db import get_db, get_test_db


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

app.dependency_overrides[get_db] = get_test_db
