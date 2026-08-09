"""The mock adapter is only useful if it replays its fixture exactly."""

import json
from pathlib import Path

import pytest

from app.adapters.transcribe.mock import DEFAULT_FIXTURES, MockTranscriber
from app.services.models import ProviderError, Transcript

RECORDED = {
    "clips": {
        "spoken.wav": {
            "text": "আমার নাম রহিম।",
            "detected_language": "bn",
            "speech_detected": True,
        },
        "quiet.wav": {"text": "", "detected_language": None, "speech_detected": False},
    }
}


@pytest.fixture
def transcriber(tmp_path: Path) -> MockTranscriber:
    path = tmp_path / "transcribe.json"
    path.write_text(json.dumps(RECORDED), encoding="utf-8")
    return MockTranscriber(path)


async def test_returns_the_recorded_response(transcriber: MockTranscriber) -> None:
    assert await transcriber.transcribe(b"", "spoken.wav", "auto") == Transcript(
        text="আমার নাম রহিম।", 
        detected_language="bn", 
        speech_detected=True
    )


async def test_replays_a_recorded_no_speech_response(
    transcriber: MockTranscriber,
) -> None:
    """A fixture saying nothing was heard must survive the round trip intact."""
    assert await transcriber.transcribe(b"", "quiet.wav", "auto") == Transcript(
        text="", 
        detected_language=None, 
        speech_detected=False
    )


async def test_ignores_the_audio_and_the_language_hint(
    transcriber: MockTranscriber,
) -> None:
    """Reacting to its input would make it something other than a replay."""
    from_bytes = await transcriber.transcribe(b"\x00\x01\x02", "spoken.wav", "en")
    from_nothing = await transcriber.transcribe(b"", "spoken.wav", "bn")
    assert from_bytes == from_nothing


async def test_unknown_filename_fails_loudly(transcriber: MockTranscriber) -> None:
    """A mock must never silently invent a transcript"""
    with pytest.raises(ProviderError) as caught:
        await transcriber.transcribe(b"", "never_recorded.wav", "auto")
    assert "never_recorded.wav" in str(caught.value)


def test_missing_fixture_file_names_the_path(tmp_path: Path) -> None:
    missing = tmp_path / "absent.json"
    with pytest.raises(ProviderError) as caught:
        MockTranscriber(missing)
    assert str(missing) in str(caught.value)


def test_shipped_fixtures_have_the_shape_the_adapter_expects() -> None:
    """Guards the real corpus, which is edited by hand when responses are recorded."""
    clips = json.loads(DEFAULT_FIXTURES.read_text(encoding="utf-8"))["clips"]
    assert clips, "the shipped fixture file has no clips"
    for filename, recorded in clips.items():
        assert set(recorded) == {"text", "detected_language", "speech_detected"}, filename
        assert isinstance(recorded["speech_detected"], bool), filename
        if not recorded["speech_detected"]:
            assert recorded["text"] == "", filename
            assert recorded["detected_language"] is None, filename
