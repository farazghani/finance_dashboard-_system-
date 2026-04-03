import pytest
from src.models.transaction import RecordCreate
from datetime import date

def test_valid_record():
    record = RecordCreate(
        amount=100,
        type="debit",
        category="food",
        date=date(2026, 4, 3)
    )

    assert record.amount == 100


def test_negative_amount():
    with pytest.raises(Exception):
        RecordCreate(
            amount=-10,
            type="debit",
            category="food",
            date=date(2026, 4, 3)
        )


def test_invalid_type():
    with pytest.raises(Exception):
        RecordCreate(
            amount=100,
            type="invalid",
            category="food",
            date=date(2026, 4, 3)
        )