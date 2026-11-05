from datetime import date

from sqlalchemy import select, func, and_

from backend.app.db.models import Car, Booking
from backend.app.db.session import SessionLocal


def check_availability(
    start_date: date,
    end_date: date,
    requested_quantity: int = 1,
    category: str | None = None,
    model: str | None = None,
    session=None,
):
    # 1. Validate the requested dates and quantity
    if start_date >= end_date:
        raise ValueError("Return date must be after pickup date.")

    if requested_quantity < 1:
        raise ValueError("Requested quantity must be at least 1.")

    # 2. Use the provided session or create a new one
    owns_session = session is None

    if owns_session:
        session = SessionLocal()

    try:
        # 3. Find overlapping confirmed bookings and sum their quantities
        overlapping_bookings = (
            select(
                Booking.car_id,
                func.sum(Booking.quantity).label("booked_quantity"),
            )
            .where(
                and_(
                    Booking.start_date < end_date,
                    Booking.end_date > start_date,
                    Booking.status == "confirmed",
                )
            )
            .group_by(Booking.car_id)
            .subquery()
        )

        # 4. Calculate the remaining quantity for each car model
        available_quantity = (
            Car.quantity
            - func.coalesce(overlapping_bookings.c.booked_quantity, 0)
        )

        # 5. Find car models with enough available vehicles
        query = (
            select(
                Car,
                available_quantity.label("available_quantity"),
            )
            .outerjoin(
                overlapping_bookings,
                Car.id == overlapping_bookings.c.car_id,
            )
            .where(available_quantity >= requested_quantity)
        )

        # 6. Apply optional model and category filters
        if category:
            query = query.where(Car.category == category)

        if model:
            query = query.where(Car.model == model)

        # 7. Execute the query and collect the results
        results = session.execute(query).all()

        return [
            {
                "car": car,
                "available_quantity": available,
            }
            for car, available in results
        ]

    finally:
        # 8. Close only sessions created by this function
        if owns_session:
            session.close()