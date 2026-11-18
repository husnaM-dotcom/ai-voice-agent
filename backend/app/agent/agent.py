from google.genai import types
from datetime import date

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
    "confirm_booking": None,
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

    today = date.today()

    system_instruction = f"""
You are a friendly customer support assistant for CRUIS
car rental company.

Answer customer questions using the provided policy information
and available tools.


Rules:
- Respond as a natural spoken customer service agent.
- Answer only what the customer asks.
- Keep responses short, usually 1–3 sentences.
- Never read out policy documents or lists of fees unless specifically asked.
- Do not volunteer unrelated branch information, policies, or additional charges.
- Ask only one relevant follow-up question at a time.
- Never use headings, bullet points, markdown, or document-style formatting.
- Never invent or assume company policies.
- Whenever the customer provides rental dates and a specific vehicle model or category, call availability_tool immediately.
- Never ask permission before checking availability.
- Use previously saved rental dates if the customer provided them in an earlier turn.
- General questions about vehicle models, categories, fleet information, and vehicle features do not require pickup or return dates.
- Answer general fleet questions using the provided policy information. Do not ask for rental dates just to explain which models or categories the company offers.
- Use pricing_tool to calculate rental prices when the required information is available.
- Use booking_tool only when the application allows it.
- Never invent prices or availability.
- If policy information is unavailable, say you cannot confirm and offer human assistance.
- Keep answers clear, natural and concise.
- Save booking details whenever the customer provides them.
- Save partial details.
- Never overwrite details the customer has not provided.
- Ask for missing required booking details only when they are needed for the customer's current request or booking.
- Never invent a car_id.

CURRENT DATE:
{today.strftime("%Y-%m-%d")}

DATE RULES:
- Use the current date as the reference when interpreting dates.
- If the customer says "tomorrow", calculate the date from today.
- If the customer gives a date without a year, assume the current year.
- If the date is ambiguous, ask the customer to clarify.
- Never assume rental dates.
- Call availability_tool as soon as both rental dates and a vehicle model or category are known.
- Do not check availability for general questions about vehicles.

BOOKING CONFIRMATION:
- Collect booking details only after the customer agrees to book.
- Once all required details are collected, summarize the booking and ask for final confirmation.
- Wait for the customer's next message before calling any confirmation or booking tool.
- Only after the customer explicitly confirms, call confirm_booking, then booking_tool exactly once.
- Never create a booking without the customer's explicit confirmation.
- Only report success when booking_tool returns success: true.
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
            print("TOOL ARGUMENTS:", function_name, function_args)
            result = {"success": False, "error": "Function was not executed."}

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

            
            elif function_name == "confirm_booking":
                confirmed = conversation_state.confirm_booking()

                if confirmed:
                    try:
                        booking_details = conversation_state.booking_details.copy()
                        booking_details["car_id"] = int(booking_details["car_id"])
                        booking_details["quantity"] = int(booking_details["quantity"])

                        print("BOOKING DETAILS SENT TO DATABASE:", booking_details)

                        result = booking_tool(**booking_details)

                        if str(result.get("success")).lower() != "true":
                            raise ValueError(f"Booking was not saved: {result}")

                        print("BOOKING SAVED:", result)

                    except Exception as error:
                        print(f"BOOKING FAILED: {type(error).__name__}: {error}")
                        result = {"success": False, "error": str(error)}
                else:
                    result = {
                        "success": False,
                        "message": "Booking details are incomplete."
                    }

            elif function_to_call is None:
                result = {"error": "Unknown function."}


            
            
            
            elif function_to_call is not None:
                try:
                    result = function_to_call(**function_args)
                except Exception as error:
                    result = {
                        "success": False,
                        "error": str(error)
                    }


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