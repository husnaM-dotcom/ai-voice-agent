
import os


from dotenv import load_dotenv
from pipecat.services.google.llm import GoogleLLMService


load_dotenv()


# Create the Gemini LLM service
def create_llm_service():

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing")

    llm = GoogleLLMService(
        api_key=api_key,
        settings=GoogleLLMService.Settings(
            model="gemini-3.5-flash-lite",
            temperature=0.2,
        ),
    )

    return llm
