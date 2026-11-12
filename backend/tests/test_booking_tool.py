
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend.app.db.models import Base, Car, Booking, Customer
from backend.app.services import booking
from backend.app.agent.tools.booking_tool import booking_tool


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    # Create a separate temporary SQLite database
    database_path = tmp_path / "test_car_rental.db"

    test_engine = create_engine(
        f"sqlite:///{database_path}"
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    # Create tables in the test database
    Base.metadata.create_all(bind=test_engine)

    # Insert a test car
    with TestSessionLocal() as session:
        car = Car(
            brand="Toyota",
            model="Yaris",
            category="Economy",
            quantity=2,
            year=2026,
            daily_rate=Decimal("40.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        session.add(car)
        session.commit()
        car_id = car.id

    # Redirect booking service to the test database
    monkeypatch.setattr(
        booking,
        "SessionLocal",
        TestSessionLocal,
    )

    yield TestSessionLocal, car_id

    test_engine.dispose()


def test_booking_is_created_in_test_database(test_db):
    TestSessionLocal, car_id = test_db

    confirmation = booking_tool(
        full_name="Test Customer",
        email="test@example.com",
        phone="+15550102000",
        driving_license_number="TEST-LICENSE-001",
        car_id=car_id,
        start_date="2026-12-01",
        end_date="2026-12-05",
        quantity=1,
    )

    # Verify the returned confirmation
    assert confirmation["booking_id"] == "1"
    assert confirmation["customer_name"] == "Test Customer"
    assert confirmation["car"] == "Toyota Yaris"
    assert confirmation["total_price"] == "160.00"
    assert confirmation["status"] == "confirmed"

    # Verify the records were actually saved
    with TestSessionLocal() as session:
        bookings = session.scalars(
            select(Booking)
        ).all()

        customers = session.scalars(
            select(Customer)
        ).all()

        assert len(bookings) == 1
        assert len(customers) == 1


def test_booking_fails_for_unavailable_car(test_db):
    TestSessionLocal, car_id = test_db

    # First booking uses both available cars
    booking_tool(
        full_name="First Customer",
        email="first@example.com",
        phone="+15550102001",
        driving_license_number="TEST-LICENSE-002",
        car_id=car_id,
        start_date="2026-12-01",
        end_date="2026-12-05",
        quantity=2,
    )

    # A further booking for the same dates must fail
    with pytest.raises(ValueError, match="not available"):
        booking_tool(
            full_name="Second Customer",
            email="second@example.com",
            phone="+15550102002",
            driving_license_number="TEST-LICENSE-003",
            car_id=car_id,
            start_date="2026-12-01",
            end_date="2026-12-05",
            quantity=1,
        )

    # Failed booking must not leave a customer record behind
    with TestSessionLocal() as session:
        bookings = session.scalars(
            select(Booking)
        ).all()

        customers = session.scalars(
            select(Customer)
        ).all()

        assert len(bookings) == 1
        assert len(customers) == 1
