from datetime import date
from decimal import Decimal

import pytest

from backend.app.services.pricing import calculate_total_price


def test_calculate_total_price():
    total = calculate_total_price(
        daily_rate=Decimal("50.00"),
        start_date=date(2026, 11, 10),
        end_date=date(2026, 11, 13),
        quantity=2,
    )

    assert total == Decimal("300.00")


def test_invalid_dates():
    with pytest.raises(ValueError):
        calculate_total_price(
            daily_rate=Decimal("50.00"),
            start_date=date(2026, 11, 13),
            end_date=date(2026, 11, 10),
        )


def test_invalid_quantity():
    with pytest.raises(ValueError):
        calculate_total_price(
            daily_rate=Decimal("50.00"),
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 13),
            quantity=0,
        )


def test_invalid_daily_rate():
    with pytest.raises(ValueError):
        calculate_total_price(
            daily_rate=Decimal("0.00"),
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 13),
        )