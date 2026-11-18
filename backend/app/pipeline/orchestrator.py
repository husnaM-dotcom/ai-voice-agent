
import asyncio
import sys

from loguru import logger

from pipecat.turns.user_stop import SpeechTimeoutUserTurnStopStrategy
from pipecat.turns.user_turn_strategies import UserTurnStrategies
from pipecat.turns.user_turn_processor import UserTurnProcessor

from pipecat.transports.local.audio import (
    LocalAudioTransport,
    LocalAudioTransportParams,
)

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineWorker
from pipecat.workers.runner import WorkerRunner

from backend.app.pipeline.vad import create_vad_processor
from backend.app.pipeline.asr import create_stt_service
from backend.app.pipeline.transcription import TranscriptionBuffer
from backend.app.pipeline.tts import tts

from backend.app.pipeline.audio_gate import (
    AudioState,
    MicrophoneGate,
    BotSpeakingMonitor,
)

logger.remove()
logger.add(sys.stderr, level="WARNING")


async def main():

    audio_state = AudioState()

    transport = LocalAudioTransport(
        params=LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        )
    )

    vad = create_vad_processor()
    stt = create_stt_service()

    pipeline = Pipeline([
        transport.input(),

        MicrophoneGate(audio_state),

        vad,
        stt,

        UserTurnProcessor(
            user_turn_strategies=UserTurnStrategies(
                stop=[
                    SpeechTimeoutUserTurnStopStrategy(
                        user_speech_timeout=3.5,
                        wait_for_transcript=True,
                    )
                ]
            )
        ),

        TranscriptionBuffer(),
        tts,

        BotSpeakingMonitor(audio_state),

        transport.output(),
    ])

    worker = PipelineWorker(pipeline)
    runner = WorkerRunner()

    await runner.add_workers(worker)
    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())
