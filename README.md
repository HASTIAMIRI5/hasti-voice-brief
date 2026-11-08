# Voice Brief

AI voice note summarizer and action extractor. Upload an audio recording or paste a transcript to get a concise summary, decisions, follow-up questions, and an actionable task list.

## Features

- Transcribe common audio formats (MP3, MP4, MPEG, MPGA, M4A, WAV, and WEBM).
- Edit the generated transcript before analysis.
- Extract action items, owners and due dates when they are stated in the note.
- Summarize decisions and surface useful follow-up questions.
- Keep your API key out of source control by loading it from the environment or Streamlit secrets.

## Requirements

- Python 3.10 or later
- An OpenAI API key with access to the configured audio and chat models

## Run locally

```bash
git clone https://github.com/HASTIAMIRI5/hasti-voice-brief.git
cd hasti-voice-brief
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in your shell or `.env`, then launch the app:

```bash
export OPENAI_API_KEY="your_api_key_here"  # macOS/Linux
streamlit run app.py
```

In Windows PowerShell, set the key with `$env:OPENAI_API_KEY="your_api_key_here"` before running `streamlit run app.py`.

The app does not load `.env` automatically. Set the environment variable in your terminal, or configure the key using Streamlit secrets (for example, in `.streamlit/secrets.toml`):

```toml
OPENAI_API_KEY = "your_api_key_here"
```

Never commit API keys or secrets to the repository.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | — | Required API credential |
| `OPENAI_AUDIO_MODEL` | `whisper-1` | Audio transcription model |
| `OPENAI_SUMMARY_MODEL` | `gpt-4o-mini` | Summary and action extraction model |

Audio uploads are limited to 25 MB, matching the transcription API's file-size limit. Text transcripts can be pasted directly, so audio transcription is optional.

## Privacy

Audio and transcript text are sent to OpenAI when you request transcription or create a brief. Do not submit sensitive information unless you are comfortable processing it with the configured provider. The app does not intentionally save your recordings or transcripts to a database.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
