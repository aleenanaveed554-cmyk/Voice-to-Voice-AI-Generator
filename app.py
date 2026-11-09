import os
import io
import base64
import html
import streamlit as st
from groq import Groq


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VoiceFlow AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, #18264a 0%, transparent 35%),
            radial-gradient(circle at top right, #35194f 0%, transparent 35%),
            linear-gradient(135deg, #070b16 0%, #0d1224 50%, #080b15 100%);
        color: white;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 35px;
        padding-bottom: 50px;
    }

    .hero {
        text-align: center;
        padding: 20px 0 15px 0;
    }

    .logo {
        width: 75px;
        height: 75px;
        margin: auto;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        background: linear-gradient(135deg, #6c5ce7, #00cec9);
        box-shadow: 0 0 45px rgba(108, 92, 231, 0.45);
    }

    .title {
        font-size: 42px;
        font-weight: 800;
        margin-top: 15px;
        color: white;
    }

    .subtitle {
        color: #aab3cf;
        font-size: 16px;
        margin-top: 5px;
    }

    .call-card {
        max-width: 850px;
        margin: 25px auto;
        padding: 35px;
        border-radius: 28px;
        background: rgba(18, 24, 45, 0.82);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow:
            0 25px 80px rgba(0,0,0,0.35),
            inset 0 1px 0 rgba(255,255,255,0.04);
        text-align: center;
    }

    .status {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 30px;
        background: rgba(0, 206, 201, 0.12);
        color: #55efc4;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 25px;
    }

    .avatar {
        width: 145px;
        height: 145px;
        margin: 10px auto 20px auto;
        border-radius: 50%;
        background:
            radial-gradient(circle at 35% 30%, #ffffff 0%, #dcd9ff 7%, transparent 8%),
            linear-gradient(135deg, #6c5ce7, #00cec9);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 62px;
        box-shadow:
            0 0 0 12px rgba(108,92,231,0.08),
            0 0 60px rgba(108,92,231,0.35);
    }

    .ai-name {
        color: white;
        font-size: 25px;
        font-weight: 700;
    }

    .ai-desc {
        color: #9ca6c2;
        margin-top: 5px;
        margin-bottom: 25px;
    }

    .feature-row {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 20px;
    }

    .feature {
        padding: 9px 15px;
        border-radius: 30px;
        background: rgba(255,255,255,0.055);
        border: 1px solid rgba(255,255,255,0.06);
        color: #b9c1d8;
        font-size: 12px;
    }

    .chat-title {
        font-size: 20px;
        font-weight: 700;
        margin: 25px 0 12px 0;
        color: white;
    }

    .user-msg {
        background: linear-gradient(135deg, #5146d9, #6c5ce7);
        color: white;
        padding: 14px 18px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0 10px auto;
        max-width: 75%;
        width: fit-content;
        box-shadow: 0 8px 25px rgba(108,92,231,0.18);
    }

    .ai-msg {
        background: rgba(255,255,255,0.065);
        color: #edf0f7;
        padding: 14px 18px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px auto 10px 0;
        max-width: 75%;
        width: fit-content;
        border: 1px solid rgba(255,255,255,0.06);
    }

    .small-label {
        color: #7f89a8;
        font-size: 11px;
        margin-bottom: 5px;
    }

    div[data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.035);
        border-radius: 16px;
    }

    .footer {
        text-align: center;
        color: #68718c;
        font-size: 12px;
        margin-top: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "call_active" not in st.session_state:
    st.session_state.call_active = False


# =========================================================
# GROQ CLIENT
# =========================================================

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="logo">🎙️</div>
        <div class="title">VoiceFlow AI</div>
        <div class="subtitle">
            Your intelligent voice conversation assistant
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# API KEY CHECK
# =========================================================

if not api_key:
    st.error(
        "GROQ_API_KEY nahi mili. Streamlit Secrets mein GROQ_API_KEY add karo."
    )
    st.stop()

client = Groq(api_key=api_key)


# =========================================================
# AI FUNCTION
# =========================================================

def get_ai_response(user_text):

    conversation = [
        {
            "role": "system",
            "content": (
                "You are VoiceFlow AI, a friendly real-time voice assistant. "
                "Talk naturally like a phone conversation. "
                "Keep responses short, clear and conversational. "
                "Do not give unnecessarily long answers. "
                "If the user speaks Urdu or Roman Urdu, reply naturally in the same style. "
                "If the user speaks English, reply in English."
            )
        }
    ]

    for message in st.session_state.messages[-10:]:
        conversation.append(message)

    conversation.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=conversation,
        temperature=0.7,
        max_tokens=350
    )

    return response.choices[0].message.content.strip()


# =========================================================
# TEXT TO SPEECH
# =========================================================

def generate_voice(text):

    try:

        # Groq Orpheus has a 200-character input limit.
        text = text[:200]

        response = client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice="autumn",
            input=text,
            response_format="wav"
        )

        audio_bytes = response.read()

        return audio_bytes

    except Exception as e:
        st.session_state.tts_error = str(e)
        return None


# =========================================================
# CALL CARD
# =========================================================

status_text = "🟢 Call Connected" if st.session_state.call_active else "⚪ Ready to Call"

st.markdown(
    f"""
    <div class="call-card">

        <div class="status">
            {status_text}
        </div>

        <div class="avatar">
            🤖
        </div>

        <div class="ai-name">
            VoiceFlow AI
        </div>

        <div class="ai-desc">
            Your personal AI voice assistant
        </div>

        <div class="feature-row">
            <div class="feature">🎙️ Voice Input</div>
            <div class="feature">🧠 AI Brain</div>
            <div class="feature">🔊 Voice Response</div>
            <div class="feature">💬 Conversation</div>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CALL BUTTONS
# =========================================================

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button(
        "📞  Start Call",
        use_container_width=True,
        type="primary",
        disabled=st.session_state.call_active
    ):
        st.session_state.call_active = True
        st.rerun()

with col2:
    if st.button(
        "🔴  End Call",
        use_container_width=True,
        disabled=not st.session_state.call_active
    ):
        st.session_state.call_active = False
        st.rerun()

with col3:
    if st.button(
        "🗑️  Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# =========================================================
# VOICE INPUT
# =========================================================

st.markdown(
    '<div class="chat-title">🎙️ Talk to VoiceFlow</div>',
    unsafe_allow_html=True
)

if st.session_state.call_active:

    st.info(
        "🎙️ Neeche microphone button dabao, bolo, phir Stop Recording karo. "
        "VoiceFlow tumhari baat samajh kar AI response dega."
    )

    audio = st.audio_input(
        "Tap to record your voice",
        key="voice_input"
    )

    if audio is not None:

        audio_bytes = audio.getvalue()

        if len(audio_bytes) > 0:

            with st.spinner("🎧 Listening..."):

                try:

                    transcription = client.audio.transcriptions.create(
                        file=(
                            "voice.webm",
                            audio_bytes
                        ),
                        model="whisper-large-v3-turbo",
                        response_format="text"
                    )

                    user_text = str(transcription).strip()

                except Exception as e:
                    st.error(f"Voice recognition error: {e}")
                    user_text = ""

            if user_text:

                # Prevent processing same recording repeatedly
                audio_hash = hash(audio_bytes)

                if st.session_state.get("last_audio_hash") != audio_hash:

                    st.session_state.last_audio_hash = audio_hash

                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "content": user_text
                        }
                    )

                    with st.spinner("🤖 VoiceFlow is thinking..."):

                        try:
                            ai_text = get_ai_response(user_text)

                        except Exception as e:
                            st.error(f"AI response error: {e}")
                            ai_text = ""

                    if ai_text:

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": ai_text
                            }
                        )

                        # Generate AI voice
                        with st.spinner("🔊 Generating AI voice..."):

                            voice_audio = generate_voice(ai_text)

                        st.rerun()


# =========================================================
# CONVERSATION
# =========================================================

if st.session_state.messages:

    st.markdown(
        '<div class="chat-title">💬 Conversation</div>',
        unsafe_allow_html=True
    )

    for message in st.session_state.messages:

        content = html.escape(message["content"])

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="small-label" style="text-align:right;">
                    You
                </div>

                <div class="user-msg">
                    {content}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="small-label">
                    VoiceFlow AI
                </div>

                <div class="ai-msg">
                    {content}
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# PLAY LAST AI AUDIO
# =========================================================

if "voice_audio" in locals() and voice_audio:

    st.markdown(
        '<div class="chat-title">🔊 AI Voice Response</div>',
        unsafe_allow_html=True
    )

    st.audio(
        voice_audio,
        format="audio/wav",
        autoplay=True
    )


# =========================================================
# TTS ERROR
# =========================================================

if "tts_error" in st.session_state:

    error_text = st.session_state.tts_error

    if "terms" in error_text.lower() or "accept" in error_text.lower():

        st.warning(
            "AI text response chal raha hai, lekin Groq voice model ke "
            "terms accept nahi hue. Groq Console mein Orpheus model ke "
            "terms accept karne ke baad voice response bhi chalega."
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        VoiceFlow AI • Powered by Groq • Speech + AI Conversation
    </div>
    """,
    unsafe_allow_html=True
)
