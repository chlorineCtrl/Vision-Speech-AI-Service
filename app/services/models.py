"""Domain objects.

These are what cross the boundaries in either direction: adapters return them,
services assemble them, routes convert them to response schemas. Nothing here
knows about HTTP, and nothing here knows which provider produced it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Transcript:
    """What a transcription provider heard in one audio file.

    Deliberately has no duration and no provider name. Keeping the fields off this class means the
    provider cannot supply it even by accident.
    """

    text: str
    detected_language: str | None
    speech_detected: bool

    @classmethod
    def no_speech(cls) -> "Transcript":
        """The silence contract, defined once so it cannot drift.

        Audio containing no speech is a valid request with an empty result,
        not an error: empty text, no detected language, and the flag that
        tells a caller the difference between silence and a failure.
        """
        return cls(text="", detected_language=None, speech_detected=False)


@dataclass(frozen=True)
class TranscriptionResult:
    """A finished transcription: what was heard, plus what we know about it."""

    transcript: Transcript
    duration_seconds: float | None
    provider: str
