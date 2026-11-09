from datetime import date
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, model_validator


class AvailabilityRequest(BaseModel):
    start_date: date
    end_date: date
    requested_quantity: int = Field(default=1, gt=0)
    category: str | None = None
    model: str | None = None


class PricingRequest(BaseModel):
    car_id: int = Field(gt=0)
    start_date: date
    end_date: date
    quantity: int = Field(default=1, gt=0)


class BookingRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    driving_license_number: str
    car_id: int = Field(gt=0)
    start_date: date
    end_date: date
    quantity: int = Field(default=1, gt=0)