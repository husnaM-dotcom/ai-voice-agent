
class ConversationState:
    def __init__(self):
        self.booking_details = {
            "full_name": None,
            "email": None,
            "phone": None,
            "driving_license_number": None,
            "car_id": None,
            "start_date": None,
            "end_date": None,
            "quantity": 1,
        }

        self.booking_confirmed = False
        self.chat_history = []

    def update_booking_details(self, details):
        self.booking_details.update(details)
        self.booking_confirmed = False

    
    def get_missing_booking_details(self):
        required_fields = [
            "full_name",
            "email",
            "phone",
            "driving_license_number",
            "car_id",
            "start_date",
            "end_date",
        ]

        return [
            field
            for field in required_fields
            if self.booking_details[field] is None
        ]

    def is_booking_ready(self):
        return len(self.get_missing_booking_details()) == 0


    def save_booking_details(
        self,
        full_name=None,
        email=None,
        phone=None,
        driving_license_number=None,
        car_id=None,
        start_date=None,
        end_date=None,
        quantity=None,
    ):
        details = {
            key: value
            for key, value in {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "driving_license_number": driving_license_number,
                "car_id": car_id,
                "start_date": start_date,
                "end_date": end_date,
                "quantity": quantity,
            }.items()
            if value is not None
        }

        if details:
            self.update_booking_details(details)
