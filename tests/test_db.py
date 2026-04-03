from src.db.db import get_test_db


def test_tables_created():
    conn = get_test_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]

    assert "users" in tables
    assert "records" in tables
    assert "audit_logs" in tables


def test_insert_record():
    conn = get_test_db()
    cursor = conn.cursor()

    # insert user first (FK)
    cursor.execute("""
        INSERT INTO users (id, name, email, password, role, created_at)
        VALUES ('u1', 'test', 'test@example.com', 'pass', 'admin', '2026-04-03')
    """)

    cursor.execute("""
        INSERT INTO records (id, user_id, amount, type, category, date, created_at)
        VALUES ('r1', 'u1', 100, 'debit', 'food', '2026-04-03', '2026-04-03')
    """)

    conn.commit()

    cursor.execute("SELECT * FROM records WHERE id='r1'")
    record = cursor.fetchone()

    assert record["amount"] == 100