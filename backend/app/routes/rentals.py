from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from backend.app.schemas.requests import AvailabilityRequest,PricingRequest,BookingRequest
from backend.app.schemas.responses import AvailableCar,PricingResponse,BookingResponse
from backend.app.services.availability import check_availability
from backend.app.services.pricing import calculate_total_price
from backend.app.services.booking import create_booking
from backend.app.db.models import Car
from backend.app.db.session import SessionLocal

router = APIRouter()


@router.post("/availability", response_model=list[AvailableCar])
def get_available_cars(request: AvailabilityRequest):

    try:
        results = check_availability(
            start_date=request.start_date,
            end_date=request.end_date,
            requested_quantity=request.requested_quantity,
            category=request.category,
            model=request.model,
        )

        return [
            {
                "car_id": item["car"].id,
                "brand": item["car"].brand,
                "model": item["car"].model,
                "category": item["car"].category,
                "daily_rate": item["car"].daily_rate,
                "available_quantity": item["available_quantity"],
            }
            for item in results
        ]

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/pricing", response_model=PricingResponse)
def get_pricing(request: PricingRequest):
    session = SessionLocal()

    try:
        car = session.scalar(
            select(Car).where(Car.id == request.car_id)
        )

        if not car:
            raise HTTPException(status_code=404, detail="Car not found")

        total = calculate_total_price(
            daily_rate=car.daily_rate,
            start_date=request.start_date,
            end_date=request.end_date,
            quantity=request.quantity,
        )

        return {"total_price": total}

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    finally:
        session.close()


@router.post("/bookings", response_model=BookingResponse)
def make_booking(request: BookingRequest):
    try:
        result = create_booking(
            full_name=request.full_name,
            email=request.email,
            phone=request.phone,
            driving_license_number=request.driving_license_number,
            car_id=request.car_id,
            start_date=request.start_date,
            end_date=request.end_date,
            quantity=request.quantity,
        )

        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))