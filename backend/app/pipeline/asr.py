import os

from dotenv import load_dotenv
from pipecat.services.deepgram.stt import DeepgramSTTService

load_dotenv()


def create_stt_service():
    api_key = os.getenv("DEEPGRAM_API_KEY")

    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY is missing")

    return DeepgramSTTService(
        api_key=api_key,
        settings=DeepgramSTTService.Settings(
            model="nova-3-general",
            language="en",
            interim_results=True,
        ),
    )