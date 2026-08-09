"""A transcriber that replays recorded provider responses from disk.
"""

import json
from pathlib import Path
from typing import Any

from app.services.models import Language, ProviderError, Transcript

_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FIXTURES = _REPO_ROOT / "testdata" / "fixtures" / "transcribe.json"


def _load_clips(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProviderError(f"Mock fixtures are missing at {path}.") from exc
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Mock fixtures at {path} are not valid JSON.") from exc
    return document["clips"]


class MockTranscriber:
    """Returns the response recorded for a filename or fails."""

    def __init__(self, fixtures_path: Path | None = None) -> None:
        self._path = fixtures_path or DEFAULT_FIXTURES
        self._clips = _load_clips(self._path)

    async def transcribe(
        self, audio: bytes, filename: str, language: Language
    ) -> Transcript:
        """Replay the exact recorded response for this file.
        """
        recorded = self._clips.get(filename)
        if recorded is None:
            raise ProviderError(
                f"No recorded response for {filename!r}. "
                f"Known clips: {', '.join(sorted(self._clips))}."
            )
        return Transcript(
            text=recorded["text"],
            detected_language=recorded["detected_language"],
            speech_detected=recorded["speech_detected"],
        )
