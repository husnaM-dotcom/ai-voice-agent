from datetime import date

from backend.app.services.booking import create_booking


def booking_tool(
    full_name: str,
    email: str,
    phone: str,
    driving_license_number: str,
    car_id: int,
    start_date: str,
    end_date: str,
    quantity: int = 1,
):
    confirmation = create_booking(
        full_name=full_name,
        email=email,
        phone=phone,
        driving_license_number=driving_license_number,
        car_id=car_id,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        quantity=quantity,
    )

    return {
        key: str(value) for key, value in confirmation.items()
    }