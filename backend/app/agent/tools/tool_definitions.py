from google.genai import types


availability_tool_definition = types.FunctionDeclaration(
    name="availability_tool",
    description="Check available car models for the requested rental dates.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "start_date": {
                "type": "STRING",
                "description": "Pickup date in YYYY-MM-DD format."
            },
            "end_date": {
                "type": "STRING",
                "description": "Return date in YYYY-MM-DD format."
            },
            "requested_quantity": {
                "type": "INTEGER",
                "description": "Number of vehicles requested."
            },
            "category": {
                "type": "STRING",
                "description": "Vehicle category, if specified."
            },
            "model": {
                "type": "STRING",
                "description": "Specific car model, if specified."
            }
        },
        "required": ["start_date", "end_date"]
    }
)


pricing_tool_definition = types.FunctionDeclaration(
    name="pricing_tool",
    description="Calculate the total rental price using the daily rate returned by the availability tool.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "daily_rate": {
                "type": "STRING",
                "description": "Daily rate returned by the availability tool."
            },
            "start_date": {
                "type": "STRING",
                "description": "Pickup date in YYYY-MM-DD format."
            },
            "end_date": {
                "type": "STRING",
                "description": "Return date in YYYY-MM-DD format."
            },
            "quantity": {
                "type": "INTEGER",
                "description": "Number of vehicles requested."
            }
        },
        "required": ["daily_rate", "start_date", "end_date"]
    }
)


booking_tool_definition = types.FunctionDeclaration(
    name="booking_tool",
    description="Create a car rental booking after the customer has explicitly confirmed all booking details.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "full_name": {
                "type": "STRING",
                "description": "Customer's full name."
            },
            "email": {
                "type": "STRING",
                "description": "Customer's email address."
            },
            "phone": {
                "type": "STRING",
                "description": "Customer's phone number."
            },
            "driving_license_number": {
                "type": "STRING",
                "description": "Customer's driving licence number."
            },
            "car_id": {
                "type": "INTEGER",
                "description": "Car ID returned by the availability tool."
            },
            "start_date": {
                "type": "STRING",
                "description": "Pickup date in YYYY-MM-DD format."
            },
            "end_date": {
                "type": "STRING",
                "description": "Return date in YYYY-MM-DD format."
            },
            "quantity": {
                "type": "INTEGER",
                "description": "Number of vehicles to book."
            }
        },
        "required": [
            "full_name",
            "email",
            "phone",
            "driving_license_number",
            "car_id",
            "start_date",
            "end_date"
        ]
    }
)

save_booking_details_definition = types.FunctionDeclaration(
    name="save_booking_details",
    description=(
        "Save any booking details the customer provides during "
        "the conversation. Call this whenever the customer provides "
        "new or corrected booking information."
    ),
    parameters={
        "type": "OBJECT",
        "properties": {
            "full_name": {"type": "STRING"},
            "email": {"type": "STRING"},
            "phone": {"type": "STRING"},
            "driving_license_number": {"type": "STRING"},
            "car_id": {"type": "INTEGER"},
            "start_date": {"type": "STRING"},
            "end_date": {"type": "STRING"},
            "quantity": {"type": "INTEGER"}
        }
    }
)


cruis_tools = [
    availability_tool_definition,
    pricing_tool_definition,
    booking_tool_definition,
    save_booking_details_definition
]