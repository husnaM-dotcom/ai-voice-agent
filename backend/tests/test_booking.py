import pytest
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from backend.app.db.models import Car, Customer, Booking
from backend.app.db.session import SessionLocal
from backend.app.services.booking import create_booking


def test_create_booking():
    session = SessionLocal()

    car = None

    try:
        # 1. Create a car for testing
        car = Car(
            brand="Toyota",
            model="Corolla",
            category="Sedan",
            quantity=5,
            year=2025,
            daily_rate=Decimal("50.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        session.add(car)
        session.commit()

        # 2. Create a booking
        confirmation = create_booking(
            full_name="Booking Test",
            email="booking_test@example.com",
            phone="0501234567",
            driving_license_number="BOOKING12345",
            car_id=car.id,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 13),
            quantity=2,
        )

        # 3. Verify the confirmation
        assert confirmation["booking_id"] is not None
        assert confirmation["customer_name"] == "Booking Test"
        assert confirmation["car"] == "Toyota Corolla"
        assert confirmation["quantity"] == 2
        assert confirmation["total_price"] == Decimal("300.00")
        assert confirmation["status"] == "confirmed"

        # 4. Verify the booking was saved in the database
        saved_booking = session.scalars(
            select(Booking).where(
                Booking.id == confirmation["booking_id"]
            )
        ).one()

        assert saved_booking.quantity == 2

        print("Booking test passed!")
        print("Booking ID:", confirmation["booking_id"])
        print("Total price: $", confirmation["total_price"])

    finally:
        session.rollback()

        if car is not None and car.id is not None:
            session.query(Booking).filter(
                Booking.car_id == car.id
            ).delete(synchronize_session=False)

            session.query(Customer).filter(
                Customer.email == "booking_test@example.com"
            ).delete(synchronize_session=False)

            session.delete(car)
            session.commit()

        session.close()


def test_unavailable_car():
    session = SessionLocal()
    car = None

    try:
        # Create a fleet containing only 2 cars
        car = Car(
            brand="Honda",
            model="Civic",
            category="Sedan",
            quantity=2,
            year=2025,
            daily_rate=Decimal("45.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        session.add(car)
        session.commit()

        # First customer books both available cars
        create_booking(
            full_name="First Customer",
            email="first@example.com",
            phone="0501111111",
            driving_license_number="FIRST123",
            car_id=car.id,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 13),
            quantity=2,
        )

        # Second customer attempts to book one more car
        try:
            create_booking(
                full_name="Second Customer",
                email="second@example.com",
                phone="0502222222",
                driving_license_number="SECOND123",
                car_id=car.id,
                start_date=date(2026, 11, 11),
                end_date=date(2026, 11, 14),
                quantity=1,
            )

            assert False, "Booking should have been rejected."

        except ValueError as error:
            assert str(error) == "The requested car is not available."

        print("Unavailable car test passed!")

    finally:
        session.rollback()

        if car is not None and car.id is not None:
            session.query(Booking).filter(
                Booking.car_id == car.id
            ).delete(synchronize_session=False)

            session.query(Customer).filter(
                Customer.email.in_([
                    "first@example.com",
                    "second@example.com",
                ])
            ).delete(synchronize_session=False)

            session.delete(car)
            session.commit()

        session.close()


def test_booking_rollback():
    session = SessionLocal()
    car = None

    try:
        # Create a fleet containing only 1 car
        car = Car(
            brand="Nissan",
            model="Altima",
            category="Sedan",
            quantity=1,
            year=2025,
            daily_rate=Decimal("55.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        session.add(car)
        session.commit()

        # First customer books the only available car
        create_booking(
            full_name="First Customer",
            email="rollback_first@example.com",
            phone="0501111111",
            driving_license_number="ROLLBACK111",
            car_id=car.id,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 13),
            quantity=1,
        )

        # Second customer attempts an unavailable booking
        try:
            create_booking(
                full_name="Second Customer",
                email="rollback_second@example.com",
                phone="0502222222",
                driving_license_number="ROLLBACK222",
                car_id=car.id,
                start_date=date(2026, 11, 11),
                end_date=date(2026, 11, 14),
                quantity=1,
            )

            assert False, "Booking should have been rejected."

        except ValueError as error:
            assert str(error) == "The requested car is not available."

        # Verify the failed customer's record was not saved
        failed_customer = session.scalars(
            select(Customer).where(
                Customer.email == "rollback_second@example.com"
            )
        ).first()

        assert failed_customer is None

        print("Booking rollback test passed!")

    finally:
        session.rollback()

        if car is not None and car.id is not None:
            session.query(Booking).filter(
                Booking.car_id == car.id
            ).delete(synchronize_session=False)

            session.query(Customer).filter(
                Customer.email.in_([
                    "rollback_first@example.com",
                    "rollback_second@example.com",
                ])
            ).delete(synchronize_session=False)

            session.delete(car)
            session.commit()

        session.close()



def test_reuse_existing_customer():
    session = SessionLocal()
    car = None

    try:
        # Create a car
        car = Car(
            brand="Hyundai",
            model="Elantra",
            category="Sedan",
            quantity=3,
            year=2025,
            daily_rate=Decimal("45.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        # Create an existing customer
        customer = Customer(
            full_name="Existing Customer",
            email="existing@example.com",
            phone="0501234567",
            driving_license_number="EXISTING123",
        )

        session.add_all([car, customer])
        session.commit()

        original_customer_id = customer.id

        # Book using the same customer's details
        confirmation = create_booking(
            full_name="Existing Customer",
            email="existing@example.com",
            phone="0501234567",
            driving_license_number="EXISTING123",
            car_id=car.id,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 12),
            quantity=1,
        )

        # Verify the existing customer was reused
        saved_customer = session.get(Customer, original_customer_id)

        assert confirmation["booking_id"] is not None
        assert saved_customer is not None

        customer_count = session.query(Customer).filter(
            Customer.email == "existing@example.com"
        ).count()

        assert customer_count == 1

        print("Existing customer test passed!")

    finally:
        session.rollback()

        if car is not None and car.id is not None:
            session.query(Booking).filter(
                Booking.car_id == car.id
            ).delete(synchronize_session=False)

            session.query(Customer).filter(
                Customer.email == "existing@example.com"
            ).delete(synchronize_session=False)

            session.delete(car)
            session.commit()

        session.close()


def test_reject_mismatched_customer_details():
    session = SessionLocal()
    car = None

    try:
        car = Car(
            brand="Kia",
            model="K5",
            category="Sedan",
            quantity=3,
            year=2025,
            daily_rate=Decimal("50.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        customer_a = Customer(
            full_name="Customer A",
            email="customer_a@example.com",
            phone="0501111111",
            driving_license_number="LICENSE_A",
        )

        customer_b = Customer(
            full_name="Customer B",
            email="customer_b@example.com",
            phone="0502222222",
            driving_license_number="LICENSE_B",
        )

        session.add_all([car, customer_a, customer_b])
        session.commit()

        # Try booking with details belonging to two different customers
        with pytest.raises(ValueError):
            create_booking(
                full_name="Customer A",
                email="customer_a@example.com",
                phone="0501111111",
                driving_license_number="LICENSE_B",
                car_id=car.id,
                start_date=date(2026, 11, 10),
                end_date=date(2026, 11, 12),
                quantity=1,
            )

        print("Mismatched customer test passed!")

    finally:
        session.rollback()

        if car is not None and car.id is not None:
            session.query(Booking).filter(
                Booking.car_id == car.id
            ).delete(synchronize_session=False)

            session.query(Customer).filter(
                Customer.email.in_([
                    "customer_a@example.com",
                    "customer_b@example.com",
                ])
            ).delete(synchronize_session=False)

            session.delete(car)
            session.commit()

        session.close()