# Voice activity detection
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.processors.audio.vad_processor import VADProcessor


def create_vad_processor():
    vad = SileroVADAnalyzer(
        params=VADParams(
            stop_secs=0.6,
        )
    )

    return VADProcessor(vad_analyzer=vad)