
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = "cars"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_car_quantity"),
        CheckConstraint("daily_rate > 0", name="check_daily_rate"),
        CheckConstraint("seats > 0", name="check_car_seats"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    daily_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    transmission: Mapped[str] = mapped_column(String(30), nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(30), nullable=False)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="car")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    driving_license_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="customer")


class Booking(Base):
    __tablename__ = "bookings"

    __table_args__ = (
        CheckConstraint("end_date > start_date", name="check_booking_dates"),
        CheckConstraint("total_price > 0", name="check_booking_price"),
        CheckConstraint("quantity > 0", name="check_booking_quantity"),
        CheckConstraint(
            "status IN ('confirmed', 'cancelled', 'completed')",
            name="check_booking_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), nullable=False
    )
    car_id: Mapped[int] = mapped_column(
        ForeignKey("cars.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="confirmed"
    )

    customer: Mapped["Customer"] = relationship(back_populates="bookings")
    car: Mapped["Car"] = relationship(back_populates="bookings")
