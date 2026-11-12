from datetime import date
from decimal import Decimal

from backend.app.services.pricing import calculate_total_price


def pricing_tool(
    daily_rate: str,
    start_date: str,
    end_date: str,
    quantity: int = 1,
):
    total = calculate_total_price(
        daily_rate=Decimal(daily_rate),
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        quantity=quantity,
    )

    return str(total)