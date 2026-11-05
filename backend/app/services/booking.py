from datetime import date
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy import select, or_

from backend.app.db.models import Customer, Car, Booking
from backend.app.db.session import SessionLocal
from backend.app.services.availability import check_availability
from backend.app.services.pricing import calculate_total_price


def get_or_create_customer(
    session,
    full_name: str,
    email: str,
    phone: str,
    driving_license_number: str,
):
    # Find customers matching either email or driving licence
    statement = select(Customer).where(
        or_(
            Customer.email == email,
            Customer.driving_license_number == driving_license_number,
        )
    )

    customers = session.scalars(statement).all()

    # No matching customer: create a new one
    if not customers:
        customer = Customer(
            full_name=full_name,
            email=email,
            phone=phone,
            driving_license_number=driving_license_number,
        )

        session.add(customer)
        session.flush()

        return customer

    # Both identifiers must belong to the same customer
    if len(customers) != 1:
        raise ValueError(
            "Email and driving licence belong to different customers."
        )

    customer = customers[0]

    if (
        customer.email != email
        or customer.driving_license_number != driving_license_number
    ):
        raise ValueError(
            "Customer email or driving licence does not match."
        )

    return customer


def create_booking(
    full_name: str,
    email: str,
    phone: str,
    driving_license_number: str,
    car_id: int,
    start_date: date,
    end_date: date,
    quantity: int = 1,
):
    session = SessionLocal()

    try:
        # 1. Acquire a SQLite write lock
        session.execute(text("BEGIN IMMEDIATE"))

        # 2. Find the requested car
        car = session.get(Car, car_id)

        if car is None:
            raise ValueError("Requested car does not exist.")

        # 3. Find or create the customer
        customer = get_or_create_customer(
            session=session,
            full_name=full_name,
            email=email,
            phone=phone,
            driving_license_number=driving_license_number,
        )

        # 4. Check car availability
        available_cars = check_availability(
            start_date=start_date,
            end_date=end_date,
            requested_quantity=quantity,
            category=car.category,
            model=car.model,
            session=session,
        )

        car_result = next(
            (
                item for item in available_cars
                if item["car"].id == car_id
            ),
            None,
        )

        if car_result is None:
            raise ValueError("The requested car is not available.")

        # 5. Calculate the booking price
        total_price = calculate_total_price(
            daily_rate=car.daily_rate,
            start_date=start_date,
            end_date=end_date,
            quantity=quantity,
        )

        # 6. Create the booking
        booking = Booking(
            customer_id=customer.id,
            car_id=car.id,
            quantity=quantity,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status="confirmed",
        )

        session.add(booking)
        session.flush()

        # 7. Prepare the confirmation details
        confirmation = {
            "booking_id": booking.id,
            "customer_name": customer.full_name,
            "car": f"{car.brand} {car.model}",
            "quantity": quantity,
            "start_date": start_date,
            "end_date": end_date,
            "total_price": total_price,
            "status": booking.status,
        }

        # 8. Save everything together
        session.commit()

        return confirmation

    except Exception:
        # Undo all database changes if anything fails
        session.rollback()
        raise

    finally:
        session.close()