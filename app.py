"""Public Streamlit webpage for agentic YouTube video summaries."""

import os

import streamlit as st
from google import genai

from youtube_utils import build_summary_prompt, normalize_youtube_url


# The model can inspect a video agentically instead of reading only a transcript.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def get_api_key() -> str | None:
    """Read the API key from hosting secrets or a local environment variable."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key

    try:
        return st.secrets.get("GEMINI_API_KEY")
    except (FileNotFoundError, KeyError):
        return None


def generate_summary(video_url: str, summary_style: str, language: str) -> tuple[str, bool]:
    """Ask Gemini to inspect the YouTube video and write a summary."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("The website owner has not configured GEMINI_API_KEY.")

    client = genai.Client(api_key=api_key)
    prompt = build_summary_prompt(summary_style, language)

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=[
            {
                "type": "video",
                "uri": video_url,
                "processing": "agentic",
            },
            {"type": "text", "text": prompt},
        ],
    )

    summary = (interaction.output_text or "").strip()
    if not summary:
        raise RuntimeError("Gemini returned an empty response. Please try another video.")

    # These step types confirm that Gemini navigated the video agentically.
    step_types = {
        getattr(step, "type", None)
        if not isinstance(step, dict)
        else step.get("type")
        for step in (getattr(interaction, "steps", None) or [])
    }
    used_agentic_processing = {
        "processing_call",
        "processing_result",
    }.issubset(step_types)

    return summary, used_agentic_processing


st.set_page_config(
    page_title="YouTube AI Summarizer",
    page_icon="▶️",
    layout="centered",
)

st.markdown(
    """
    <style>
    
        .block-container { max-width: 850px; padding-top: 3rem; }
        .hero {
            padding: 2rem;
            border-radius: 22px;
            background: linear-gradient(135deg, #111827, #312e81);
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 16px 40px rgba(17, 24, 39, 0.18);
        }
        .hero h1 { margin: 0 0 0.5rem 0; font-size: 2.2rem; }
        .hero p { margin: 0; color: #dbeafe; font-size: 1.05rem; }
        .result-label { font-size: 1.35rem; font-weight: 700; margin-top: 1.5rem; }
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            height: 3rem;
            font-weight: 700;
        }
    </style>
    <div class="hero">
        <h1>YouTube AI Summarizer</h1>
        <p>Paste a public YouTube link. Gemini will inspect the video and create clear notes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("summary_form"):
    raw_url = st.text_input(
        "YouTube video link",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    left, right = st.columns(2)
    with left:
        summary_style = st.selectbox(
            "Summary type",
            ["Study notes", "Detailed summary", "Quick summary"],
        )
    with right:
        language = st.selectbox(
            "Output language",
            ["English", "Hindi"],
        )

    submitted = st.form_submit_button("Generate Summary", type="primary")

if submitted:
    clean_url = normalize_youtube_url(raw_url)

    if not clean_url:
        st.error("Please enter a valid YouTube video link.")
    else:
        with st.spinner("The AI agent is inspecting the video. This can take a minute..."):
            try:
                summary, agentic_verified = generate_summary(
                    clean_url,
                    summary_style,
                    language,
                )
            except Exception as exc:
                message = str(exc)
                if "public" in message.lower() or "permission" in message.lower():
                    st.error("This video cannot be accessed. Please use a public YouTube video.")
                elif "quota" in message.lower() or "429" in message:
                    st.error("The API limit has been reached. Please try again later.")
                else:
                    st.error(f"Could not summarize this video: {message}")
            else:
                st.success("Summary generated successfully.")
                if agentic_verified:
                    st.caption("Agentic processing verified: Gemini navigated the video timeline.")
                else:
                    st.caption("Gemini processed the video using the requested agentic mode.")

                st.markdown('<div class="result-label">Your Summary</div>', unsafe_allow_html=True)
                st.markdown(summary)
                st.download_button(
                    "Download summary",
                    data=summary,
                    file_name="youtube_summary.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

st.caption("Only public YouTube videos are supported. The Gemini API key stays on the server.")
