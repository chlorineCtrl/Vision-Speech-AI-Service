"""Application entrypoint: builds the FastAPI app and wires it together."""

from fastapi import FastAPI

app = FastAPI(
    title="vision-speech-ai-service",
    description="Audio transcription and lab report extraction.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe. Deliberately does not touch the provider."""
    return {"status": "ok"}
