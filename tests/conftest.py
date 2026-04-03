import pytest
from httpx import AsyncClient
from src.main import app
from src.db.db import get_db, get_test_db


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

app.dependency_overrides[get_db] = get_test_db