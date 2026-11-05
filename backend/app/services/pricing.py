from datetime import date
from decimal import Decimal


def calculate_total_price(
    daily_rate: Decimal,
    start_date: date,
    end_date: date,
    quantity: int = 1,
) -> Decimal:

    # Validate the inputs
    if start_date >= end_date:
        raise ValueError("Return date must be after pickup date.")

    if daily_rate <= 0:
        raise ValueError("Daily rate must be greater than zero.")

    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")

    # Calculate rental duration
    rental_days = (end_date - start_date).days

    # Calculate total rental price
    total_price = daily_rate * rental_days * quantity

    return total_price.quantize(Decimal("0.01"))