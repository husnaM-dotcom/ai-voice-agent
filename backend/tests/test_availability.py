import pytest
from datetime import date
from decimal import Decimal

from backend.app.db.models import Car, Customer, Booking
from backend.app.db.session import SessionLocal
from backend.app.services.availability import check_availability
from backend.app.services.booking import create_booking


def test_check_availability():
    session = SessionLocal()

    car = None
    customer = None

    try:
        # 1. Create a car with 10 vehicles in the fleet
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

        # 2. Create a test customer
        customer = Customer(
            full_name="Availability Test",
            email="availability_test@example.com",
            phone="0501234567",
            driving_license_number="AVAIL12345",
        )

        session.add_all([car, customer])
        session.flush()

        # 3. Create two overlapping confirmed bookings
        booking_1 = Booking(
            car=car,
            customer=customer,
            quantity=2,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 13),
            total_price=Decimal("900.00"),
            status="confirmed",
        )

        booking_2 = Booking(
            car=car,
            customer=customer,
            quantity=3,
            start_date=date(2026, 11, 12),
            end_date=date(2026, 11, 15),
            total_price=Decimal("1350.00"),
            status="confirmed",
        )

        session.add_all([booking_1, booking_2])

        # Save test records so the availability service can read them
        session.commit()

        # 4. Check availability for November 11–14
        results = check_availability(
            start_date=date(2026, 11, 11),
            end_date=date(2026, 11, 14),
            requested_quantity=4,
            model="Corolla",
        )

        # 5. Find our test car in the results
        car_result = next(
            (
                result
                for result in results
                if result["car"].id == car.id
            ),
            None,
        )

        # 6. Verify the result
        assert car_result is not None
        assert car_result["available_quantity"] == 5

        print("Availability test passed!")
        print("Total fleet: 10")
        print("Booked vehicles: 5")
        print("Available vehicles:", car_result["available_quantity"])

    finally:
        # 7. Remove test records so the database stays clean
        session.rollback()

        if car is not None and car.id is not None:
            session.query(Booking).filter(
                Booking.car_id == car.id
            ).delete(synchronize_session=False)

            session.delete(customer)
            session.delete(car)
            session.commit()

        session.close()





def test_cancelled_booking():
    session = SessionLocal()

    car = None
    customer = None

    try:
        # 1. Create a car with 10 vehicles
        car = Car(
            brand="Honda",
            model="Civic",
            category="Sedan",
            quantity=10,
            year=2025,
            daily_rate=Decimal("180.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        # 2. Create a customer
        customer = Customer(
            full_name="Cancelled Test",
            email="cancelled_test@example.com",
            phone="0501234567",
            driving_license_number="CANCEL123",
        )

        session.add_all([car, customer])
        session.flush()

        # 3. Create a cancelled booking for 3 cars
        booking = Booking(
            car=car,
            customer=customer,
            quantity=3,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 15),
            total_price=Decimal("2700.00"),
            status="cancelled",
        )

        session.add(booking)
        session.commit()

        # 4. Check availability
        results = check_availability(
            start_date=date(2026, 11, 11),
            end_date=date(2026, 11, 14),
            requested_quantity=1,
            model="Civic",
        )

        # 5. Verify all 10 cars are available
        car_result = next(
            (
                result
                for result in results
                if result["car"].id == car.id
            ),
            None,
        )

        assert car_result is not None
        assert car_result["available_quantity"] == 10

        print("Cancelled booking test passed!")
        print("Available vehicles:", car_result["available_quantity"])

    finally:
        session.rollback()

        if car is not None and car.id is not None:
            session.query(Booking).filter(
                Booking.car_id == car.id
            ).delete(synchronize_session=False)

            session.delete(customer)
            session.delete(car)
            session.commit()

        session.close()

def test_return_date():
    session = SessionLocal()

    try:
        car = Car(
            brand="Honda",
            model="Accord",
            category="Sedan",
            quantity=10,
            year=2025,
            daily_rate=Decimal("200.00"),
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
        )

        customer = Customer(
            full_name="Return Date Test",
            email="return_date_test@example.com",
            phone="0501234567",
            driving_license_number="RETURN12345",
        )

        # Existing booking: November 10 to November 12
        booking = Booking(
            car=car,
            customer=customer,
            quantity=4,
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 12),
            total_price=Decimal("1600.00"),
            status="confirmed",
        )

        session.add(booking)
        session.commit()

        # New customer requests November 12 to November 15
        results = check_availability(
            start_date=date(2026, 11, 12),
            end_date=date(2026, 11, 15),
            requested_quantity=7,
            model="Accord",
        )

        car_result = next(
            (item for item in results if item["car"].id == car.id),
            None,
        )

        assert car_result is not None
        assert car_result["available_quantity"] == 10

        print("Return date test passed!")
        print("Available vehicles:", car_result["available_quantity"])

    finally:
        session.rollback()

        if car.id is not None:
            session.query(Booking).filter(
                Booking.car_id == car.id
            ).delete(synchronize_session=False)

        session.delete(customer)
        session.delete(car)
        session.commit()
        session.close()



def test_invalid_dates():
    with pytest.raises(ValueError):
        check_availability(
            start_date=date(2026, 11, 15),
            end_date=date(2026, 11, 10),
        )

    print("Invalid dates test passed!")


def test_invalid_quantity():
    with pytest.raises(ValueError):
        check_availability(
            start_date=date(2026, 11, 10),
            end_date=date(2026, 11, 15),
            requested_quantity=0,
        )

    print("Invalid quantity test passed!")


if __name__ == "__main__":
    test_check_availability()
    test_cancelled_booking()
    test_return_date()
    test_invalid_dates()
    test_invalid_quantity()



def test_seeded_inventory():
    results = check_availability(
        start_date=date(2026, 11, 20),
        end_date=date(2026, 11, 23),
        requested_quantity=1,
        category="Economy",
    )

    assert len(results) > 0

    print("Seeded inventory test passed!")
    for result in results:
        print(
            result["car"].brand,
            result["car"].model,
            "Available:",
            result["available_quantity"],
        )

def test_booking_reduces_inventory():
    session = SessionLocal()
    car = None

    try:
        car = session.query(Car).filter(
            Car.model == "Yaris"
        ).first()

        assert car is not None

        car_id = car.id

    finally:
        session.close()

    try:
        create_booking(
            full_name="Inventory Test",
            email="inventory_test@example.com",
            phone="0501234567",
            driving_license_number="INVENTORY123",
            car_id=car_id,
            start_date=date(2026, 11, 20),
            end_date=date(2026, 11, 23),
            quantity=1,
        )

        results = check_availability(
            start_date=date(2026, 11, 20),
            end_date=date(2026, 11, 23),
            category="Economy",
            model="Yaris",
        )

        car_result = next(
            item for item in results
            if item["car"].id == car_id
        )

        assert car_result["available_quantity"] == 1

    finally:
        session = SessionLocal()

        customer = session.query(Customer).filter_by(
            email="inventory_test@example.com"
        ).first()

        if customer:
            session.query(Booking).filter_by(
                customer_id=customer.id
            ).delete()
            session.delete(customer)

        session.commit()
        session.close()