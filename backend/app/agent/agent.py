from google.genai import types

from backend.app.rag.embeddings import client
from backend.app.rag.retriever import retrieve_relevant_chunks

from backend.app.agent.tools.availability_tool import availability_tool
from backend.app.agent.tools.pricing_tool import pricing_tool
from backend.app.agent.tools.booking_tool import booking_tool
from backend.app.agent.tools.tool_definitions import cruis_tools
from backend.app.agent.conversation import ConversationState

available_functions = {
    "availability_tool": availability_tool,
    "pricing_tool": pricing_tool,
    "booking_tool": booking_tool,
    "save_booking_details": None,
}


def answer_customer_question(question, conversation_state=None):

    if conversation_state is None:
        conversation_state = ConversationState()

    try:
        relevant_chunks = retrieve_relevant_chunks(question)
    except Exception:
        relevant_chunks = []

    context = "\n\n".join(relevant_chunks) if relevant_chunks else (
        "No relevant policy information was found."
    )

    system_instruction = f"""
You are a friendly customer support assistant for CRUIS
car rental company.

Answer customer questions using the provided policy information
and available tools.

Rules:
- Never invent or assume company policies.
- Use availability_tool to check vehicle availability.
- Use pricing_tool to calculate rental prices.
- Use booking_tool only when the application allows it.
- Never invent prices or availability.
- If policy information is unavailable, say you cannot confirm
  and offer human assistance.
- Keep answers clear, natural and concise.
- Save booking details whenever the customer provides them.
- Save partial details.
- Never overwrite details the customer has not provided.
- Ask for missing required booking details.
- Never invent a car_id.

CURRENT BOOKING DETAILS:
{conversation_state.booking_details}

MISSING BOOKING DETAILS:
{conversation_state.get_missing_booking_details()}

CRUIS POLICY INFORMATION:
{context}
"""

    chat = client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            tools=[
                types.Tool(function_declarations=cruis_tools)
            ],
        ),
        history=conversation_state.chat_history,
    )

    try:
        response = chat.send_message(question)
    except Exception:
        return "I'm sorry, I'm having trouble processing your request right now. Please try again or contact CRUIS support."

    while response.function_calls:
        function_responses = []

        for function_call in response.function_calls:
            function_name = function_call.name
            function_args = dict(function_call.args)

            function_to_call = available_functions.get(function_name)

            if function_name == "save_booking_details":
                try:
                    conversation_state.save_booking_details(**function_args)
                    result = {
                        "success": True,
                        "booking_details": conversation_state.booking_details,
                        "missing_details": conversation_state.get_missing_booking_details()
                    }
                except Exception as error:
                    result = {"error": str(error)}

            elif function_to_call is None:
                result = {"error": "Unknown function."}

            elif function_name == "booking_tool" and (
                not conversation_state.booking_confirmed
                or not conversation_state.is_booking_ready()
            ):
                result = {
                    "error": "Booking not permitted. Explicit customer confirmation and all required details are needed."
                }

            else:
                try:
                    result = function_to_call(**function_args)
                except Exception as error:
                    result = {"error": str(error)}

            function_responses.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": result},
                )
            )

        try:
            response = chat.send_message(function_responses)
        except Exception:
            return "I'm sorry, I couldn't complete your request. Please try again or contact CRUIS support."

    conversation_state.chat_history = chat.get_history()

    return response.text