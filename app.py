import os
import io
import base64
import tempfile

import streamlit as st
from groq import Groq

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VoiceFlow AI",
    page_icon="🎙️",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #111827, #1e1b4b);
        color: white;
    }

    .title {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        margin-top: 20px;
    }

    .subtitle {
        text-align: center;
        color: #cbd5e1;
        font-size: 18px;
        margin-bottom: 35px;
    }

    .box {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
    }

    .response {
        background: rgba(255,255,255,0.08);
        border-left: 4px solid #8b5cf6;
        border-radius: 15px;
        padding: 20px;
        font-size: 17px;
        line-height: 1.7;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 50px;
        font-size: 17px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="title">🎙️ VoiceFlow AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Talk naturally with your AI voice assistant</div>',
    unsafe_allow_html=True
)

# =========================================================
# API KEY
# =========================================================

api_key = None

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

if not api_key:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Groq API key nahi mili.")
    st.info(
        "Streamlit Secrets mein GROQ_API_KEY add karo."
    )
    st.stop()

client = Groq(api_key=api_key)

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## ⚙️ Settings")

    model = st.selectbox(
        "AI Model",
        [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile"
        ],
        index=0
    )

    st.markdown("---")

    st.markdown("### 🎤 How it works")

    st.write("1. Voice record karo")
    st.write("2. AI tumhari voice samjhega")
    st.write("3. AI response generate karega")
    st.write("4. Response voice mein suno")

    st.markdown("---")

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.last_response = ""
        st.rerun()

# =========================================================
# MAIN AREA
# =========================================================

col1, col2 = st.columns(2)

# =========================================================
# VOICE INPUT
# =========================================================

with col1:

    st.markdown(
        '<div class="box"><h2>🎤 Voice Input</h2>',
        unsafe_allow_html=True
    )

    audio = st.audio_input("🎙️ Record your voice")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# PROCESS VOICE
# =========================================================

if audio is not None:

    st.success("✅ Voice recorded successfully!")

    audio_bytes = audio.getvalue()

    with st.spinner("🎧 Voice ko samajh raha hoon..."):

        try:

            # -------------------------------------------------
            # SAVE AUDIO TEMPORARILY
            # -------------------------------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav"
            ) as temp_audio:

                temp_audio.write(audio_bytes)
                audio_path = temp_audio.name

            # -------------------------------------------------
            # SPEECH TO TEXT
            # -------------------------------------------------

            with open(audio_path, "rb") as file:

                transcription = client.audio.transcriptions.create(
                    file=file,
                    model="whisper-large-v3-turbo",
                    response_format="text"
                )

            user_text = str(transcription)

            st.markdown("### 🗣️ You said")

            st.info(user_text)

            # -------------------------------------------------
            # AI RESPONSE
            # -------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_text
                }
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly voice AI assistant. "
                            "Give natural, helpful and concise answers. "
                            "Speak like a real conversational assistant."
                        )
                    }
                ] + st.session_state.messages,
                temperature=0.7,
                max_tokens=500
            )

            ai_text = response.choices[0].message.content

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": ai_text
                }
            )

            st.session_state.last_response = ai_text

            st.markdown("### 🤖 AI Response")

            st.markdown(
                f'<div class="response">{ai_text}</div>',
                unsafe_allow_html=True
            )

            # -------------------------------------------------
            # TEXT TO SPEECH
            # -------------------------------------------------

            with st.spinner("🔊 AI voice bana raha hai..."):

                speech_response = client.audio.speech.create(
                    model="canopylabs/orpheus-v1-english",
                    voice="tara",
                    input=ai_text,
                    response_format="wav"
                )

                audio_output = speech_response.read()

            st.markdown("### 🔊 AI Voice")

            st.audio(
                audio_output,
                format="audio/wav"
            )

            # -------------------------------------------------
            # DOWNLOAD
            # -------------------------------------------------

            st.download_button(
                label="⬇️ Download AI Voice",
                data=audio_output,
                file_name="voiceflow_ai_response.wav",
                mime="audio/wav"
            )

        except Exception as e:

            st.error("❌ Error")

            st.code(str(e))

# =========================================================
# CHAT HISTORY
# =========================================================

if st.session_state.messages:

    st.markdown("---")
    st.markdown("## 💬 Conversation")

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="box">
                    <b>🗣️ You</b><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="response">
                    <b>🤖 AI</b><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#94a3b8;">
        🎙️ VoiceFlow AI • Powered by Groq
    </div>
    """,
    unsafe_allow_html=True
)
