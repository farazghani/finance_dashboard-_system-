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

    return {
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense,
        "category_breakdown": categories,
    }