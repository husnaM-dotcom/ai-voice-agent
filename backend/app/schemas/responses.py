from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class AvailableCar(BaseModel):
    car_id: int
    brand: str
    model: str
    category: str
    daily_rate: Decimal
    available_quantity: int


class PricingResponse(BaseModel):
    total_price: Decimal


class BookingResponse(BaseModel):
    booking_id: int
    customer_name: str
    car: str
    quantity: int
    start_date: date
    end_date: date
    total_price: Decimal
    status: str