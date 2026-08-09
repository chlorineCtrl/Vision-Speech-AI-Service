"""What this service requires of a provider stated as protocols.
"""

from typing import Protocol

from app.services.models import Language, Transcript


class Transcriber(Protocol):
    """Turns the bytes of an audio file into a Transcript."""

    async def transcribe(
        self, audio: bytes, filename: str, language: Language
    ) -> Transcript: ...
