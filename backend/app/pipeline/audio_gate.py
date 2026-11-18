
from dataclasses import dataclass
import asyncio

from pipecat.frames.frames import (
    InputAudioRawFrame,
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import (
    FrameProcessor,
)


@dataclass
class AudioState:
    bot_speaking: bool = False


class MicrophoneGate(FrameProcessor):

    def __init__(self, state):
        super().__init__()
        self.state = state

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        if (
            isinstance(frame, InputAudioRawFrame)
            and self.state.bot_speaking
        ):
            return

        await self.push_frame(frame, direction)


class BotSpeakingMonitor(FrameProcessor):

    def __init__(self, state):
        super().__init__()
        self.state = state

    async def release_microphone(self):
        await asyncio.sleep(0.5)
        self.state.bot_speaking = False
        print("\nMicrophone active. You can speak.")

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        if isinstance(frame, BotStartedSpeakingFrame):
            self.state.bot_speaking = True
            print("\nAgent speaking. Microphone temporarily muted.")

        elif isinstance(frame, BotStoppedSpeakingFrame):
            self.create_task(
                self.release_microphone(),
                name="release-microphone",
            )

        await self.push_frame(frame, direction)
