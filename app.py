import os
import io
import base64
import time
import queue
import textwrap

import av
import numpy as np
import streamlit as st
from groq import Groq
from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode,
    RTCConfiguration,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VoiceFlow AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# HTML HELPER
# =========================================================

def html(content):
    """Remove accidental indentation so HTML renders correctly."""
    st.markdown(
        textwrap.dedent(content),
        unsafe_allow_html=True,
    )


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

* {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 15%, rgba(99,102,241,0.25), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(6,182,212,0.20), transparent 30%),
        radial-gradient(circle at 50% 90%, rgba(168,85,247,0.18), transparent 35%),
        #050816;

    color: white;
}

header {
    visibility: hidden;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

.hero {
    text-align: center;
    padding: 40px 20px 25px;
}

.logo {
    width: 82px;
    height: 82px;
    margin: auto;
    border-radius: 25px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 38px;

    background:
        linear-gradient(135deg, #6366f1, #06b6d4);

    box-shadow:
        0 0 55px rgba(99,102,241,0.50);
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 58px;
    font-weight: 700;
    margin: 18px 0 5px;

    background:
        linear-gradient(90deg, #ffffff, #93c5fd, #c4b5fd);

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #9ca9c2;
    font-size: 17px;
    max-width: 720px;
    margin: auto;
}

.status {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin: 22px 0 35px;
}

.status-item {
    padding: 8px 16px;
    border-radius: 50px;

    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);

    color: #cbd5e1;
    font-size: 13px;
}

.card {
    background: rgba(15,23,42,0.72);

    border: 1px solid rgba(148,163,184,0.15);

    border-radius: 25px;

    padding: 28px;

    margin-bottom: 22px;

    box-shadow:
        0 20px 80px rgba(0,0,0,0.25);

    backdrop-filter: blur(20px);
}

.card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
}

.card-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-top: 7px;
}

.live-box {
    text-align: center;

    padding: 45px 20px;

    border-radius: 22px;

    background:
        radial-gradient(
            circle,
            rgba(99,102,241,0.16),
            rgba(2,6,23,0.5)
        );

    border: 1px solid rgba(99,102,241,0.25);
}

.live-icon {
    font-size: 65px;
    animation: pulse 1.7s infinite;
}

@keyframes pulse {

    0% {
        transform: scale(1);
        opacity: 0.7;
    }

    50% {
        transform: scale(1.08);
        opacity: 1;
    }

    100% {
        transform: scale(1);
        opacity: 0.7;
    }

}

.live-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 25px;
    font-weight: 700;
    margin-top: 10px;
}

.live-text {
    color: #94a3b8;
    margin-top: 8px;
}

.stButton > button {
    width: 100%;
    min-height: 54px;

    border-radius: 15px;

    border: 1px solid rgba(255,255,255,0.12);

    background:
        linear-gradient(135deg, #6366f1, #4f46e5);

    color: white;

    font-size: 16px;
    font-weight: 700;

    transition: 0.2s;
}

.stButton > button:hover {
    transform: translateY(-2px);

    box-shadow:
        0 15px 40px rgba(99,102,241,0.35);
}

.user-msg {
    background: rgba(79,70,229,0.18);

    border:
        1px solid rgba(99,102,241,0.25);

    padding: 17px;

    border-radius: 18px;

    margin: 12px 0;
}

.ai-msg {
    background: rgba(14,165,233,0.10);

    border:
        1px solid rgba(14,165,233,0.20);

    padding: 17px;

    border-radius: 18px;

    margin: 12px 0;
}

.label {
    color: #93c5fd;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 1px;

    text-transform: uppercase;

    margin-bottom: 7px;
}

.footer {
    text-align: center;

    color: #64748b;

    margin-top: 45px;

    font-size: 13px;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# GROQ CLIENT
# =========================================================

def get_client():

    api_key = None

    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)


client = get_client()


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "latest_voice" not in st.session_state:
    st.session_state.latest_voice = None


# =========================================================
# HERO
# =========================================================

html(
    """
    <div class="hero">
        <div class="logo">🎙️</div>

        <h1>VoiceFlow AI</h1>

        <p>
            Talk naturally with your AI assistant.
            No typing. No sending. Just speak and listen.
        </p>
    </div>

    <div class="status">

        <div class="status-item">
            🎤 Live Voice
        </div>

        <div class="status-item">
            🧠 Groq AI
        </div>

        <div class="status-item">
            🔊 AI Voice
        </div>

        <div class="status-item">
            <span style="color:#86efac;">●</span>
            Ready
        </div>

    </div>
    """
)


# =========================================================
# API CHECK
# =========================================================

if client is None:

    st.error(
        "❌ GROQ_API_KEY is missing. "
        "Please add GROQ_API_KEY to your Streamlit secrets."
    )

    st.stop()


# =========================================================
# CONVERSATION FUNCTIONS
# =========================================================

def transcribe_audio(audio_bytes):

    result = client.audio.transcriptions.create(
        file=("voice.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="json",
        temperature=0,
    )

    return result.text.strip()


def generate_ai_response(user_text):

    messages = [
        {
            "role": "system",
            "content": """
You are VoiceFlow AI, a friendly real-time voice assistant.

Speak naturally like a human conversation.

Keep answers short and conversational because your
response will be spoken aloud.

Do not give unnecessarily long explanations.
""",
        }
    ]

    for message in st.session_state.messages[-8:]:

        messages.append(
            {
                "role": message["role"],
                "content": message["text"],
            }
        )

    messages.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()


def generate_voice(text):

    speech_text = text[:200]

    response = client.audio.speech.create(
        model="canopylabs/orpheus-v1-english",
        voice="autumn",
        input=speech_text,
        response_format="wav",
    )

    return response.read()


def audio_to_wav(audio_frames):

    if not audio_frames:
        return None

    samples = []

    for frame in audio_frames:

        array = frame.to_ndarray()

        if array.ndim > 1:
            array = array[0]

        samples.append(array)

    if not samples:
        return None

    audio = np.concatenate(samples)

    audio = np.asarray(audio)

    if np.issubdtype(audio.dtype, np.floating):

        audio = np.clip(
            audio * 32767,
            -32768,
            32767,
        ).astype(np.int16)

    else:

        audio = np.clip(
            audio,
            -32768,
            32767,
        ).astype(np.int16)

    buffer = io.BytesIO()

    container = av.open(
        buffer,
        mode="w",
        format="wav",
    )

    stream = container.add_stream(
        "pcm_s16le",
        rate=16000,
    )

    stream.layout = "mono"

    frame = av.AudioFrame.from_ndarray(
        audio.reshape(1, -1),
        format="s16",
        layout="mono",
    )

    frame.sample_rate = 16000

    for packet in stream.encode(frame):
        container.mux(packet)

    for packet in stream.encode():
        container.mux(packet)

    container.close()

    return buffer.getvalue()


# =========================================================
# MAIN LAYOUT
# =========================================================

left, right = st.columns(
    [1, 1],
    gap="large",
)


# =========================================================
# LEFT SIDE
# =========================================================

with left:

    html(
        """
        <div class="card">

            <div class="card-title">
                🎙️ Live Voice Conversation
            </div>

            <div class="card-subtitle">
                Talk naturally. VoiceFlow AI will listen and respond.
            </div>

            <br>

            <div class="live-box">

                <div class="live-icon">
                    🎙️
                </div>

                <div class="live-title">
                    Ready to Talk
                </div>

                <div class="live-text">
                    Start the microphone and speak naturally.
                </div>

            </div>

        </div>
        """
    )


    # =====================================================
    # WEBRTC CONFIG
    # =====================================================

    RTC_CONFIGURATION = RTCConfiguration(
        {
            "iceServers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302"
                    ]
                }
            ]
        }
    )


    # =====================================================
    # WEBRTC
    # =====================================================

    ctx = webrtc_streamer(
        key="voiceflow-live",
        mode=WebRtcMode.SENDONLY,

        audio_receiver_size=1024,

        rtc_configuration=RTC_CONFIGURATION,

        media_stream_constraints={
            "video": False,
            "audio": True,
        },
    )


    # =====================================================
    # LIVE AUDIO PROCESSING
    # =====================================================

    if ctx.state.playing:

        st.success(
            "🟢 Microphone is active — Speak now"
        )

        status_placeholder = st.empty()

        audio_frames = []

        silence_counter = 0

        speech_started = False

        while ctx.state.playing:

            try:

                frames = ctx.audio_receiver.get_frames(
                    timeout=1
                )

            except queue.Empty:

                continue

            for frame in frames:

                audio_frames.append(frame)

                try:

                    audio_array = frame.to_ndarray()

                    volume = np.sqrt(
                        np.mean(
                            np.square(
                                audio_array.astype(
                                    np.float32
                                )
                            )
                        )
                    )

                except Exception:

                    volume = 0

                # -----------------------------------------
                # SPEECH DETECTION
                # -----------------------------------------

                if volume > 500:

                    speech_started = True

                    silence_counter = 0

                    status_placeholder.info(
                        "🎤 Listening..."
                    )

                elif speech_started:

                    silence_counter += 1

                # -----------------------------------------
                # END OF SPEECH
                # -----------------------------------------

                if (
                    speech_started
                    and silence_counter > 12
                    and len(audio_frames) > 15
                ):

                    status_placeholder.warning(
                        "🧠 Understanding you..."
                    )

                    try:

                        wav_bytes = audio_to_wav(
                            audio_frames
                        )

                        if wav_bytes:

                            user_text = transcribe_audio(
                                wav_bytes
                            )

                            if user_text:

                                st.session_state.messages.append(
                                    {
                                        "role": "user",
                                        "text": user_text,
                                    }
                                )

                                status_placeholder.info(
                                    "🤖 AI is thinking..."
                                )

                                ai_text = generate_ai_response(
                                    user_text
                                )

                                st.session_state.messages.append(
                                    {
                                        "role": "assistant",
                                        "text": ai_text,
                                    }
                                )

                                status_placeholder.info(
                                    "🔊 AI is speaking..."
                                )

                                voice_bytes = generate_voice(
                                    ai_text
                                )

                                st.session_state.latest_voice = (
                                    voice_bytes
                                )

                                st.rerun()

                    except Exception as e:

                        st.error(
                            "❌ Voice processing error: "
                            + str(e)
                        )

                    audio_frames = []

                    silence_counter = 0

                    speech_started = False


# =========================================================
# RIGHT SIDE — CONVERSATION
# =========================================================

with right:

    html(
        """
        <div class="card">

            <div class="card-title">
                🤖 AI Conversation
            </div>

            <div class="card-subtitle">
                Your live conversation with VoiceFlow AI.
            </div>

        </div>
        """
    )


    if st.session_state.messages:

        for message in st.session_state.messages:

            safe_text = (
                message["text"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            if message["role"] == "user":

                html(
                    f"""
                    <div class="user-msg">

                        <div class="label">
                            You
                        </div>

                        {safe_text}

                    </div>
                    """
                )

            else:

                html(
                    f"""
                    <div class="ai-msg">

                        <div class="label">
                            VoiceFlow AI
                        </div>

                        {safe_text}

                    </div>
                    """
                )

    else:

        html(
            """
            <div class="live-box">

                <div style="font-size:50px;">
                    💬
                </div>

                <div class="live-title">
                    Conversation Ready
                </div>

                <div class="live-text">
                    Start the microphone and begin speaking.
                </div>

            </div>
            """
        )


# =========================================================
# AI VOICE RESPONSE
# =========================================================

if st.session_state.latest_voice:

    html(
        """
        <div class="card">

            <div class="card-title">
                🔊 AI Voice Response
            </div>

            <div class="card-subtitle">
                Voice response generated by VoiceFlow AI.
            </div>

        </div>
        """
    )

    audio_data = st.session_state.latest_voice

    audio_base64 = base64.b64encode(
        audio_data
    ).decode()

    st.markdown(
        f"""
        <audio
            controls
            autoplay
            style="width:100%;">

            <source
                src="data:audio/wav;base64,{audio_base64}"
                type="audio/wav">

        </audio>
        """,
        unsafe_allow_html=True,
    )

    st.download_button(
        "⬇️ Download AI Voice",
        data=audio_data,
        file_name="voiceflow_ai_response.wav",
        mime="audio/wav",
        use_container_width=True,
    )


# =========================================================
# CLEAR CONVERSATION
# =========================================================

if st.session_state.messages:

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.session_state.latest_voice = None

        st.rerun()


# =========================================================
# FEATURES
# =========================================================

html(
    """
    <br><br>

    <div class="card">

        <div style="
            text-align:center;
            font-family:'Space Grotesk';
            font-size:26px;
            font-weight:700;
            margin-bottom:25px;">
            Voice AI Experience
        </div>

        <div style="
            display:grid;
            grid-template-columns:repeat(3,1fr);
            gap:20px;">

            <div style="text-align:center;padding:15px;">

                <div style="font-size:30px;">
                    🎤
                </div>

                <div style="font-weight:700;margin-top:8px;">
                    Live Listening
                </div>

                <div style="color:#94a3b8;font-size:13px;margin-top:5px;">
                    Speak naturally without pressing Send.
                </div>

            </div>


            <div style="text-align:center;padding:15px;">

                <div style="font-size:30px;">
                    🧠
                </div>

                <div style="font-weight:700;margin-top:8px;">
                    Groq Intelligence
                </div>

                <div style="color:#94a3b8;font-size:13px;margin-top:5px;">
                    Fast AI responses for natural conversations.
                </div>

            </div>


            <div style="text-align:center;padding:15px;">

                <div style="font-size:30px;">
                    🔊
                </div>

                <div style="font-weight:700;margin-top:8px;">
                    Voice Reply
                </div>

                <div style="color:#94a3b8;font-size:13px;margin-top:5px;">
                    AI answers through generated speech.
                </div>

            </div>

        </div>

    </div>
    """
)


# =========================================================
# FOOTER
# =========================================================

html(
    """
    <div class="footer">

        VoiceFlow AI

        <br>

        Built with Python • Streamlit • Groq • WebRTC

        <br>

        Natural Voice • AI Conversation • Hands-Free Experience

    </div>
    """
)
