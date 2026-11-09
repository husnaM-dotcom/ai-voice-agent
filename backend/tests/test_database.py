
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from backend.app.db.models import Car, Customer, Booking
from backend.app.db.session import SessionLocal


def test_database_operations():
    session = SessionLocal()

    try:
        # 1. Create a car
        car = Car(
            brand="Toyota",
            model="Corolla",
            category="Sedan",
            quantity=10,
            year=2025,
            daily_rate=Decimal("150.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        # 2. Create a customer
        customer = Customer(
            full_name="Test Customer",
            email="database_test_2026@example.com",
            phone="0501234567",
            driving_license_number="DATABASE_TEST_123",
        )

        # 3. Create a booking connecting the car and customer
        booking = Booking(
            car=car,
            customer=customer,
            quantity=2,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 13),
            total_price=Decimal("900.00"),
            status="confirmed",
        )

        session.add(booking)
        session.flush()

        # 4. Retrieve the booking from the database
        saved_booking = session.scalars(
            select(Booking).where(Booking.id == booking.id)
        ).one()

        # 5. Check the saved information
        print("Booking ID:", saved_booking.id)
        print("Customer:", saved_booking.customer.full_name)
        print("Car:", saved_booking.car.brand, saved_booking.car.model)
        print("Quantity:", saved_booking.quantity)
        print("Total price:", saved_booking.total_price)

        print("\nDatabase operations successful!")

    finally:
        # Undo test changes so the real database stays clean
        session.rollback()
        session.close()


if __name__ == "__main__":
    test_database_operations()
