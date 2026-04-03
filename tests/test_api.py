from datetime import date, datetime

import pytest

from src.core.security import create_access_token, get_password_hash
from src.db.db import get_db, get_test_db
from src.main import app
from src.models.user import Role


@pytest.fixture
def shared_db():
    db = get_test_db()

    def override_get_db():
        return db

    app.dependency_overrides[get_db] = override_get_db
    yield db
    app.dependency_overrides[get_db] = get_test_db
    db.close()


def seed_user(db, user_id: str, email: str, role: str = "admin"):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO users (id, name, email, password, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            "Seed User",
            email,
            get_password_hash("secret"),
            role,
            datetime.utcnow().isoformat(),
        ),
    )
    db.commit()


def auth_headers(role: Role, user_id: str = "auth-user", email: str = "auth@example.com"):
    token = create_access_token(user_id=user_id, email=email, role=role)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_user_endpoint(client, shared_db):
    response = await client.post(
        "/users",
        json={
            "name": "Faraz",
            "email": "faraz@example.com",
            "password": "secret123",
            "role": "admin",
        },
        headers=auth_headers(Role.admin),
    )

    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_login_user_endpoint(client, shared_db):
    create_response = await client.post(
        "/users",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "secret123",
            "role": "admin",
        },
        headers=auth_headers(Role.admin),
    )
    assert create_response.status_code == 201

    response = await client.post(
        "/users/login",
        json={
            "email": "login@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


@pytest.mark.asyncio
async def test_login_user_endpoint_rejects_invalid_credentials(client, shared_db):
    seed_user(shared_db, "user-login-1", "invalid-login@example.com")

    response = await client.post(
        "/users/login",
        json={
            "email": "invalid-login@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_user_endpoint_rejects_inactive_user(client, shared_db):
    await client.post(
        "/users",
        json={
            "name": "Inactive User",
            "email": "inactive@example.com",
            "password": "secret123",
            "role": "viewer",
            "is_active": False,
        },
        headers=auth_headers(Role.admin),
    )

    response = await client.post(
        "/users/login",
        json={
            "email": "inactive@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_endpoint(client, shared_db):
    seed_user(shared_db, "user-1", "user1@example.com")

    response = await client.patch(
        "/users/user-1",
        json={"name": "Updated User"},
        headers=auth_headers(Role.admin),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated User"


@pytest.mark.asyncio
async def test_update_user_endpoint_can_deactivate_user(client, shared_db):
    seed_user(shared_db, "user-1b", "user1b@example.com")

    response = await client.patch(
        "/users/user-1b",
        json={"is_active": False},
        headers=auth_headers(Role.admin),
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_records_endpoints(client, shared_db):
    seed_user(shared_db, "admin-1", "admin@example.com")

    create_response = await client.post(
        "/users/admin-1/records",
        json={
            "amount": 125.5,
            "type": "credit",
            "category": "salary",
            "date": str(date(2026, 4, 4)),
            "notes": "monthly pay",
        },
        headers=auth_headers(Role.admin, user_id="admin-1", email="admin@example.com"),
    )

    assert create_response.status_code == 201
    record_id = create_response.json()["id"]

    list_response = await client.get(
        "/records",
        headers=auth_headers(Role.analyst, user_id="analyst-1", email="analyst@example.com"),
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = await client.patch(
        f"/records/{record_id}",
        json={"notes": "updated note"},
        headers=auth_headers(Role.admin, user_id="admin-1", email="admin@example.com"),
    )

    assert update_response.status_code == 200
    assert update_response.json()["notes"] == "updated note"


@pytest.mark.asyncio
async def test_records_endpoint_filters_by_type_category_and_date(client, shared_db):
    seed_user(shared_db, "filter-user-1", "filter1@example.com")

    await client.post(
        "/users/filter-user-1/records",
        json={
            "amount": 100,
            "type": "credit",
            "category": "salary",
            "date": str(date(2026, 4, 4)),
        },
        headers=auth_headers(Role.admin, user_id="admin-filter", email="adminfilter@example.com"),
    )
    await client.post(
        "/users/filter-user-1/records",
        json={
            "amount": 40,
            "type": "debit",
            "category": "food",
            "date": str(date(2026, 4, 5)),
        },
        headers=auth_headers(Role.admin, user_id="admin-filter", email="adminfilter@example.com"),
    )

    type_response = await client.get(
        "/records?type=credit",
        headers=auth_headers(Role.analyst, user_id="analyst-filter", email="analystfilter@example.com"),
    )
    category_response = await client.get(
        "/records?category=food",
        headers=auth_headers(Role.analyst, user_id="analyst-filter", email="analystfilter@example.com"),
    )
    date_response = await client.get(
        "/records?date=2026-04-05",
        headers=auth_headers(Role.analyst, user_id="analyst-filter", email="analystfilter@example.com"),
    )

    assert type_response.status_code == 200
    assert len(type_response.json()) == 1
    assert type_response.json()[0]["type"] == "credit"

    assert category_response.status_code == 200
    assert len(category_response.json()) == 1
    assert category_response.json()[0]["category"] == "food"

    assert date_response.status_code == 200
    assert len(date_response.json()) == 1
    assert date_response.json()[0]["date"] == "2026-04-05"


@pytest.mark.asyncio
async def test_dashboard_summary_endpoint(client, shared_db):
    seed_user(shared_db, "user-2", "user2@example.com")

    await client.post(
        "/users/user-2/records",
        json={
            "amount": 200,
            "type": "credit",
            "category": "salary",
            "date": str(date(2026, 4, 4)),
        },
        headers=auth_headers(Role.admin, user_id="admin-2", email="admin2@example.com"),
    )
    await client.post(
        "/users/user-2/records",
        json={
            "amount": 50,
            "type": "debit",
            "category": "food",
            "date": str(date(2026, 4, 4)),
        },
        headers=auth_headers(Role.admin, user_id="admin-2", email="admin2@example.com"),
    )
    await client.post(
        "/users/user-2/records",
        json={
            "amount": 120,
            "type": "credit",
            "category": "freelance",
            "date": str(date(2026, 3, 15)),
            "notes": "project payout",
        },
        headers=auth_headers(Role.admin, user_id="admin-2", email="admin2@example.com"),
    )

    response = await client.get(
        "/dashboard/summary",
        headers=auth_headers(Role.viewer, user_id="viewer-1", email="viewer@example.com"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_income"] == 320
    assert body["total_expense"] == 50
    assert body["net_balance"] == 270
    assert len(body["recent_activity"]) == 3
    assert body["recent_activity"][0]["date"] == "2026-04-04"
    assert len(body["monthly_trends"]) == 2
    assert body["monthly_trends"][0]["month"] == "2026-04"
    assert body["monthly_trends"][0]["total_income"] == 200
    assert body["monthly_trends"][0]["total_expense"] == 50


@pytest.mark.asyncio
async def test_get_audit_logs_endpoint_requires_admin(client, shared_db):
    await client.post(
        "/users",
        json={
            "name": "Audit Admin",
            "email": "user3@example.com",
            "password": "secret123",
            "role": "admin",
        },
        headers=auth_headers(Role.admin),
    )

    admin_token = create_access_token(
        user_id="user-3",
        email="user3@example.com",
        role=Role.admin,
    )
    response = await client.get(
        "/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_audit_logs_endpoint_forbids_non_admin(client, shared_db):
    seed_user(shared_db, "user-4", "user4@example.com", role="viewer")

    viewer_token = create_access_token(
        user_id="user-4",
        email="user4@example.com",
        role=Role.viewer,
    )
    response = await client.get(
        "/audit-logs",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_endpoint_forbids_non_admin(client, shared_db):
    response = await client.post(
        "/users",
        json={
            "name": "Blocked User",
            "email": "blocked@example.com",
            "password": "secret123",
            "role": "viewer",
        },
        headers=auth_headers(Role.viewer, user_id="viewer-2", email="viewer2@example.com"),
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_record_endpoint_forbids_analyst(client, shared_db):
    seed_user(shared_db, "record-owner-1", "owner@example.com")

    response = await client.post(
        "/users/record-owner-1/records",
        json={
            "amount": 80,
            "type": "debit",
            "category": "food",
            "date": str(date(2026, 4, 4)),
        },
        headers=auth_headers(Role.analyst, user_id="analyst-2", email="analyst2@example.com"),
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_records_endpoint_forbids_unauthenticated(client, shared_db):
    response = await client.get("/records")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_summary_endpoint_allows_analyst(client, shared_db):
    response = await client.get(
        "/dashboard/summary",
        headers=auth_headers(Role.analyst, user_id="analyst-3", email="analyst3@example.com"),
    )

    assert response.status_code == 200
