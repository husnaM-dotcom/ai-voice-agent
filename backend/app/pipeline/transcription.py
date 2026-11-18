
import asyncio
import time

from pipecat.frames.frames import (
    InterimTranscriptionFrame,
    TranscriptionFrame,
    STTMetadataFrame,
    UserStoppedSpeakingFrame,
    TTSSpeakFrame,
)

from pipecat.processors.frame_processor import (
    FrameProcessor,
    FrameDirection,
)

from backend.app.agent.agent import answer_customer_question
from backend.app.agent.conversation import ConversationState


class TranscriptionBuffer(FrameProcessor):

    def __init__(self):
        super().__init__()
        self.transcript_parts = []
        self.conversation_state = ConversationState()

    async def get_gemini_response(self, transcript):
        start_time = time.perf_counter()

        print("\nWaiting for Gemini...")

        try:
            response = await asyncio.to_thread(
                answer_customer_question,
                transcript,
                self.conversation_state,
            )

            print(f"\nAGENT: {response}\n")

            print(
                "BOOKING DETAILS:",
                self.conversation_state.booking_details,
            )

            print(
                f"Gemini response time: "
                f"{time.perf_counter() - start_time:.2f} seconds\n"
            )

            await self.push_frame(
                TTSSpeakFrame(
                    response,
                    append_to_context=False,
                ),
                FrameDirection.DOWNSTREAM,
            )

        except Exception as error:
            print(f"AGENT ERROR: {error}")

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        if isinstance(frame, InterimTranscriptionFrame):
            print(f"\rYOU: {frame.text}", end="", flush=True)

        elif isinstance(frame, STTMetadataFrame):
            print(
                f"STT P99 LATENCY: "
                f"{frame.ttfs_p99_latency} seconds"
            )

        elif isinstance(frame, TranscriptionFrame):
            self.transcript_parts.append(frame.text)

        elif isinstance(frame, UserStoppedSpeakingFrame):
            transcript = " ".join(self.transcript_parts).strip()
            self.transcript_parts.clear()

            if transcript:
                print(f"\nYOU: {transcript}")

                self.create_task(
                    self.get_gemini_response(transcript),
                    name="gemini-response",
                )

        await self.push_frame(frame, direction)
