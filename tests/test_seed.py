from src.db.db import get_test_db
from src.db.seed import seed_database


def test_seed_database_inserts_sample_data():
    db = get_test_db()

    summary = seed_database(db)

    assert summary == {"users": 3, "records": 4, "audit_logs": 3}

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM users")
    assert cursor.fetchone()["count"] == 3

    cursor.execute("SELECT COUNT(*) AS count FROM records")
    assert cursor.fetchone()["count"] == 4

    cursor.execute("SELECT COUNT(*) AS count FROM audit_logs")
    assert cursor.fetchone()["count"] == 3


def test_seed_database_is_idempotent():
    db = get_test_db()

    seed_database(db)
    seed_database(db)

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM users")
    assert cursor.fetchone()["count"] == 3

    cursor.execute("SELECT COUNT(*) AS count FROM records")
    assert cursor.fetchone()["count"] == 4

    cursor.execute("SELECT COUNT(*) AS count FROM audit_logs")
    assert cursor.fetchone()["count"] == 3
