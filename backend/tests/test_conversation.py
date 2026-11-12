from backend.app.agent.conversation import ConversationState
from backend.app.agent.agent import answer_customer_question

def test_booking_details_start_empty():
    state = ConversationState()

    assert state.get_missing_booking_details()
    assert state.is_booking_ready() is False


def test_booking_details_can_be_updated():
    state = ConversationState()

    state.update_booking_details({
        "full_name": "Test Customer",
        "email": "test@example.com",
        "phone": "123456789",
        "driving_license_number": "TEST123",
        "car_id": 1,
        "start_date": "2026-12-01",
        "end_date": "2026-12-05",
    })

    assert state.is_booking_ready() is True


def test_updating_details_resets_confirmation():
    state = ConversationState()
    state.booking_confirmed = True

    state.update_booking_details({"start_date": "2026-12-02"})

    assert state.booking_confirmed is False


def test_save_partial_booking_details():
    state = ConversationState()

    state.save_booking_details(
        full_name="John Smith",
        start_date="2026-12-01"
    )

    assert state.booking_details["full_name"] == "John Smith"
    assert state.booking_details["start_date"] == "2026-12-01"
    assert state.booking_details["email"] is None


def test_saving_new_details_preserves_existing_details():
    state = ConversationState()

    state.save_booking_details(full_name="John Smith")
    state.save_booking_details(email="john@example.com")

    assert state.booking_details["full_name"] == "John Smith"
    assert state.booking_details["email"] == "john@example.com"



def test_booking_details_persist_across_messages():
    state = ConversationState()

    state.save_booking_details(
        start_date="2026-12-01",
        end_date="2026-12-05"
    )

    state.save_booking_details(
        full_name="John Smith"
    )

    assert state.booking_details["start_date"] == "2026-12-01"
    assert state.booking_details["end_date"] == "2026-12-05"
    assert state.booking_details["full_name"] == "John Smith"



    
def test_agent_saves_booking_details_across_messages():
    state = ConversationState()

    answer_customer_question(
        "I want to rent an economy car from December 1 to December 5, 2026.",
        state
    )

    answer_customer_question(
        "My name is John Smith and my email is john@example.com.",
        state
    )

    assert state.booking_details["start_date"] == "2026-12-01"
    assert state.booking_details["end_date"] == "2026-12-05"
    assert state.booking_details["full_name"] == "John Smith"
    assert state.booking_details["email"] == "john@example.com"