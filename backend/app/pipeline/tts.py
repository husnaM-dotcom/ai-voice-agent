
import os

from dotenv import load_dotenv
from pipecat.services.deepgram.flux.tts import DeepgramFluxTTSService


load_dotenv()

tts = DeepgramFluxTTSService(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
    settings=DeepgramFluxTTSService.Settings(
        voice="flux-brooke-en",
    ),
)
