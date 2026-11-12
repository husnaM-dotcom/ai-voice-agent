from datetime import date

from backend.app.services.availability import check_availability


def availability_tool(
    start_date: str,
    end_date: str,
    requested_quantity: int = 1,
    category: str | None = None,
    model: str | None = None,
):
    results = check_availability(
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        requested_quantity=requested_quantity,
        category=category,
        model=model,
    )

    return [
        {   "car_id": result["car"].id,
            "brand": result["car"].brand,
            "model": result["car"].model,
            "category": result["car"].category,
            "daily_rate": str(result["car"].daily_rate),
            "available_quantity": result["available_quantity"],
            "seats": result["car"].seats,
            "transmission": result["car"].transmission,
        }
        for result in results
    ]