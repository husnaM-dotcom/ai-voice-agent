import asyncio

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineWorker
from pipecat.workers.runner import WorkerRunner

from pipecat.transports.local.audio import (
    LocalAudioTransport,
    LocalAudioTransportParams,
)

from pipecat.frames.frames import TTSSpeakFrame

from backend.app.agent.agent import answer_customer_question
from backend.app.pipeline.tts import tts


async def main():

    question = "Where is your branch located?"

    print("CUSTOMER:", question)

    response = await asyncio.to_thread(
        answer_customer_question,
        question,
    )

    print("AGENT:", response)

    transport = LocalAudioTransport(
        params=LocalAudioTransportParams(
            audio_out_enabled=True,
        )
    )

    pipeline = Pipeline([
        tts,
        transport.output(),
    ])

    worker = PipelineWorker(pipeline)
    runner = WorkerRunner()

    pipeline_started = asyncio.Event()

    @worker.event_handler("on_pipeline_started")
    async def on_pipeline_started(worker, frame):
        pipeline_started.set()

    await runner.add_workers(worker)

    runner_task = asyncio.create_task(runner.run())

    await pipeline_started.wait()

    await worker.queue_frame(
        TTSSpeakFrame(
            response,
            append_to_context=False,
        )
    )

    await worker.end()
    await runner_task


if __name__ == "__main__":
    asyncio.run(main())