"""Streamlit app for turning voice notes into concise, actionable briefs."""

from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st
from openai import OpenAI

AUDIO_MODEL = os.getenv("OPENAI_AUDIO_MODEL", "whisper-1")
SUMMARY_MODEL = os.getenv("OPENAI_SUMMARY_MODEL", "gpt-4o-mini")
MAX_AUDIO_BYTES = 25 * 1024 * 1024
AUDIO_TYPES = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]


def get_api_key() -> str | None:
    """Read the API key from the environment or Streamlit secrets."""
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("OPENAI_API_KEY")
    except Exception:
        # Streamlit raises when no secrets file is configured.
        return None


def get_client() -> OpenAI:
    key = get_api_key()
    if not key:
        raise ValueError(
            "Add OPENAI_API_KEY to your environment or Streamlit secrets to continue."
        )
    return OpenAI(api_key=key)


def transcribe_audio(audio: Any) -> str:
    """Transcribe an uploaded audio file with OpenAI's audio API."""
    if audio.size > MAX_AUDIO_BYTES:
        raise ValueError("Audio files must be 25 MB or smaller.")
    response = get_client().audio.transcriptions.create(
        model=AUDIO_MODEL,
        file=(audio.name, audio.getvalue(), audio.type or "application/octet-stream"),
    )
    return response.text.strip()


def analyze_transcript(transcript: str) -> dict[str, Any]:
    """Return a structured brief from a transcript."""
    response = get_client().chat.completions.create(
        model=SUMMARY_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You turn voice-note transcripts into accurate, concise briefs. "
                    "Do not invent facts, owners, or deadlines. Return valid JSON with "
                    "these keys: title (string), summary (string), action_items "
                    "(array of objects with task, owner, due_date), decisions (array "
                    "of strings), and follow_up_questions (array of strings). Use null "
                    "for unknown owners or due dates. If there are no actions, return "
                    "an empty action_items array."
                ),
            },
            {
                "role": "user",
                "content": f"Create a brief from this transcript:\n\n{transcript}",
            },
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("The AI returned an empty response. Please try again.")
    result = json.loads(content)
    if not isinstance(result, dict):
        raise ValueError("The AI returned an unexpected response. Please try again.")
    return result


def display_brief(brief: dict[str, Any]) -> None:
    title = brief.get("title")
    if isinstance(title, str) and title.strip():
        st.subheader(title)

    summary = brief.get("summary")
    if isinstance(summary, str) and summary.strip():
        st.markdown("### Summary")
        st.write(summary)

    actions = brief.get("action_items", [])
    if isinstance(actions, list):
        st.markdown("### Action items")
        if not actions:
            st.write("No action items found.")
        for item in actions:
            if isinstance(item, dict):
                task = item.get("task", "Action item")
                details = []
                if item.get("owner"):
                    details.append(f"Owner: {item['owner']}")
                if item.get("due_date"):
                    details.append(f"Due: {item['due_date']}")
                st.markdown(f"- **{task}**" + (f" — {' · '.join(details)}" if details else ""))
            elif isinstance(item, str):
                st.markdown(f"- {item}")

    for key, heading in (
        ("decisions", "Decisions"),
        ("follow_up_questions", "Follow-up questions"),
    ):
        values = brief.get(key, [])
        if isinstance(values, list) and values:
            st.markdown(f"### {heading}")
            for value in values:
                st.markdown(f"- {value}")


st.set_page_config(page_title="Voice Brief", page_icon="🎙️", layout="centered")
st.title("🎙️ Voice Brief")
st.caption("Turn a voice note into a clear summary and a practical action list.")

with st.expander("How it works"):
    st.write(
        "Upload a recording to transcribe it, or paste a transcript below. "
        "Review and edit the transcript before generating the brief."
    )

audio = st.file_uploader("Upload a voice note", type=AUDIO_TYPES)
if st.button("Transcribe audio", disabled=audio is None, use_container_width=True):
    try:
        with st.spinner("Transcribing your recording…"):
            st.session_state["transcript"] = transcribe_audio(audio)
        st.success("Transcription ready. You can edit it below.")
    except Exception as exc:
        st.error(str(exc))

transcript = st.text_area(
    "Transcript",
    key="transcript",
    height=220,
    placeholder="Paste a transcript here, or upload audio above and transcribe it.",
)

if st.button("Create my brief", type="primary", use_container_width=True):
    if not transcript.strip():
        st.warning("Add a transcript before creating a brief.")
    else:
        try:
            with st.spinner("Creating your summary and action items…"):
                st.session_state["brief"] = analyze_transcript(transcript.strip())
        except json.JSONDecodeError:
            st.error("The AI response could not be read. Please try again.")
        except Exception as exc:
            st.error(str(exc))

if "brief" in st.session_state:
    st.divider()
    display_brief(st.session_state["brief"])
