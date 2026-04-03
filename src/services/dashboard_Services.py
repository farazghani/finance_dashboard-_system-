def get_dashboard_summary(db):
    cursor = db.cursor()

    # total income
    cursor.execute("SELECT SUM(amount) as total FROM records WHERE type='credit'")
    income = cursor.fetchone()["total"] or 0

    # total expense
    cursor.execute("SELECT SUM(amount) as total FROM records WHERE type='debit'")
    expense = cursor.fetchone()["total"] or 0

    # category breakdown
    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM records
        GROUP BY category
    """)
    categories = [
        {"category": row["category"], "total": row["total"]}
        for row in cursor.fetchall()
    ]

    cursor.execute(
        """
        SELECT id, user_id, amount, type, category, date, notes
        FROM records
        ORDER BY date DESC, created_at DESC
        LIMIT 5
        """
    )
    recent_activity = [
        {
            "id": row["id"],
            "user_id": row["user_id"],
            "amount": row["amount"],
            "type": row["type"],
            "category": row["category"],
            "date": row["date"],
            "notes": row["notes"],
        }
        for row in cursor.fetchall()
    ]

    cursor.execute(
        """
        SELECT
            substr(date, 1, 7) as month,
            SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'debit' THEN amount ELSE 0 END) as total_expense
        FROM records
        GROUP BY substr(date, 1, 7)
        ORDER BY month DESC
        LIMIT 12
        """
    )
    monthly_trends = [
        {
            "month": row["month"],
            "total_income": row["total_income"] or 0,
            "total_expense": row["total_expense"] or 0,
            "net_balance": (row["total_income"] or 0) - (row["total_expense"] or 0),
        }
        for row in cursor.fetchall()
    ]

    return {
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense,
        "category_breakdown": categories,
        "recent_activity": recent_activity,
        "monthly_trends": monthly_trends,
    }
