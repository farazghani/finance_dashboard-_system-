from datetime import UTC, date, datetime, timedelta

from src.core.security import get_password_hash
from src.db.db import get_connection
from src.db.migration import create_tables


def _iso_now(offset_days: int = 0) -> str:
    return (datetime.now(UTC) + timedelta(days=offset_days)).isoformat()


SEED_USERS = [
    {
        "id": "seed-admin-1",
        "name": "Admin User",
        "email": "admin@zorvyn.dev",
        "password": get_password_hash("admin123"),
        "role": "admin",
        "is_active": 1,
        "created_at": _iso_now(-10),
    },
    {
        "id": "seed-analyst-1",
        "name": "Analyst User",
        "email": "analyst@zorvyn.dev",
        "password": get_password_hash("analyst123"),
        "role": "analyst",
        "is_active": 1,
        "created_at": _iso_now(-8),
    },
    {
        "id": "seed-viewer-1",
        "name": "Viewer User",
        "email": "viewer@zorvyn.dev",
        "password": get_password_hash("viewer123"),
        "role": "viewer",
        "is_active": 1,
        "created_at": _iso_now(-6),
    },
]

SEED_RECORDS = [
    {
        "id": "seed-record-1",
        "user_id": "seed-admin-1",
        "amount": 5000.0,
        "type": "credit",
        "category": "salary",
        "date": date(2026, 4, 1).isoformat(),
        "notes": "monthly salary",
        "created_at": _iso_now(-3),
    },
    {
        "id": "seed-record-2",
        "user_id": "seed-admin-1",
        "amount": 1200.0,
        "type": "debit",
        "category": "rent",
        "date": date(2026, 4, 2).isoformat(),
        "notes": "apartment rent",
        "created_at": _iso_now(-2),
    },
    {
        "id": "seed-record-3",
        "user_id": "seed-analyst-1",
        "amount": 320.5,
        "type": "debit",
        "category": "food",
        "date": date(2026, 4, 3).isoformat(),
        "notes": "groceries",
        "created_at": _iso_now(-1),
    },
    {
        "id": "seed-record-4",
        "user_id": "seed-analyst-1",
        "amount": 850.0,
        "type": "credit",
        "category": "freelance",
        "date": date(2026, 4, 4).isoformat(),
        "notes": "project payment",
        "created_at": _iso_now(0),
    },
]

SEED_AUDIT_LOGS = [
    {
        "id": "seed-audit-1",
        "user_id": "seed-admin-1",
        "action": "SEED_CREATE_USER",
        "target_id": "seed-admin-1",
        "details": "Seeded admin user",
        "created_at": _iso_now(-10),
    },
    {
        "id": "seed-audit-2",
        "user_id": "seed-admin-1",
        "action": "SEED_CREATE_RECORD",
        "target_id": "seed-record-1",
        "details": "Seeded salary record",
        "created_at": _iso_now(-3),
    },
    {
        "id": "seed-audit-3",
        "user_id": "seed-analyst-1",
        "action": "SEED_CREATE_RECORD",
        "target_id": "seed-record-4",
        "details": "Seeded freelance record",
        "created_at": _iso_now(0),
    },
]


def seed_database(conn) -> dict[str, int]:
    create_tables(conn)
    cursor = conn.cursor()

    for user in SEED_USERS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (id, name, email, password, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                user["name"],
                user["email"],
                user["password"],
                user["role"],
                user["is_active"],
                user["created_at"],
            ),
        )

    for record in SEED_RECORDS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO records
            (id, user_id, amount, type, category, date, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["id"],
                record["user_id"],
                record["amount"],
                record["type"],
                record["category"],
                record["date"],
                record["notes"],
                record["created_at"],
            ),
        )

    for audit_log in SEED_AUDIT_LOGS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO audit_logs
            (id, user_id, action, target_id, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                audit_log["id"],
                audit_log["user_id"],
                audit_log["action"],
                audit_log["target_id"],
                audit_log["details"],
                audit_log["created_at"],
            ),
        )

    conn.commit()

    return {
        "users": len(SEED_USERS),
        "records": len(SEED_RECORDS),
        "audit_logs": len(SEED_AUDIT_LOGS),
    }


def main():
    conn = get_connection()
    try:
        summary = seed_database(conn)
    finally:
        conn.close()

    print(
        "Seeded database with "
        f"{summary['users']} users, "
        f"{summary['records']} records, "
        f"and {summary['audit_logs']} audit logs."
    )


if __name__ == "__main__":
    main()
