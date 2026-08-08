# vision-speech-ai-service

Take-home exercise for Celloscope Limited. Two HTTP endpoints:

- `POST /api/v1/transcribe` — audio (Bengali/English) → transcript
- `POST /api/v1/documents/extract` — photo of an English lab report → structured JSON

Both endpoints call a pretrained provider (Gemini Flash) through an adapter layer,
and both ship with mock adapters so the service runs and tests pass with no API key.

Full documentation follows in a later commit. See `DECISIONS.md` for design
choices and `LIMITATIONS.md` for known gaps.
