"""Application entrypoint: builds the FastAPI app and wires it together."""

import logging

from fastapi import FastAPI

from app.api.errors import register_error_handlers

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="vision-speech-ai-service",
    description="Audio transcription and lab report extraction.",
    version="0.1.0",
)

register_error_handlers(app)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe. Deliberately does not touch the provider."""
    return {"status": "ok"}
