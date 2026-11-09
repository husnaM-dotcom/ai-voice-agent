from backend.app.db.models import Car
from backend.app.db.session import SessionLocal

cars = [
    # Economy
    {
        "brand": "Toyota",
        "model": "Yaris",
        "category": "Economy",
        "quantity": 2,
        "year": 2024,
        "daily_rate": 40,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 4,
    },
    {
        "brand": "Kia",
        "model": "Picanto",
        "category": "Economy",
        "quantity": 2,
        "year": 2024,
        "daily_rate": 40,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 4,
    },

        # Compact
    {
        "brand": "Honda",
        "model": "Civic",
        "category": "Compact",
        "quantity": 2,
        "year": 2024,
        "daily_rate": 46,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },
    {
        "brand": "Volkswagen",
        "model": "Golf",
        "category": "Compact",
        "quantity": 1,
        "year": 2024,
        "daily_rate": 46,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },

    # Midsize sedan
    {
        "brand": "Toyota",
        "model": "Camry",
        "category": "Midsize sedan",
        "quantity": 2,
        "year": 2024,
        "daily_rate": 58,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },
    {
        "brand": "Hyundai",
        "model": "Sonata",
        "category": "Midsize sedan",
        "quantity": 1,
        "year": 2024,
        "daily_rate": 58,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },

    # SUV
    {
        "brand": "Toyota",
        "model": "RAV4",
        "category": "SUV",
        "quantity": 2,
        "year": 2024,
        "daily_rate": 75,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },
    {
        "brand": "Nissan",
        "model": "Rogue",
        "category": "SUV",
        "quantity": 1,
        "year": 2024,
        "daily_rate": 75,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },

    # Minivan
    {
        "brand": "Kia",
        "model": "Carnival",
        "category": "Minivan",
        "quantity": 1,
        "year": 2024,
        "daily_rate": 95,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 7,
    },
    {
        "brand": "Chrysler",
        "model": "Pacifica",
        "category": "Minivan",
        "quantity": 1,
        "year": 2024,
        "daily_rate": 95,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 7,
    },

    # Premium
    {
        "brand": "BMW",
        "model": "5 Series",
        "category": "Premium",
        "quantity": 2,
        "year": 2024,
        "daily_rate": 130,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },
    {
        "brand": "Mercedes-Benz",
        "model": "E-Class",
        "category": "Premium",
        "quantity": 1,
        "year": 2024,
        "daily_rate": 130,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },
    {
        "brand": "BMW",
        "model": "X5",
        "category": "Premium",
        "quantity": 1,
        "year": 2024,
        "daily_rate": 130,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },
    {
        "brand": "Mercedes-Benz",
        "model": "GLE",
        "category": "Premium",
        "quantity": 1,
        "year": 2024,
        "daily_rate": 130,
        "transmission": "Automatic",
        "fuel_type": "Petrol",
        "seats": 5,
    },
]


def seed_cars():
    session = SessionLocal()

    try:
        for car_data in cars:
            car = Car(**car_data)
            session.add(car)

        session.commit()
        print("Car inventory seeded successfully!")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    seed_cars()