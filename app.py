import os
import io
import base64
import streamlit as st
from groq import Groq

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="VoiceFlow AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

* {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(99,102,241,0.20), transparent 30%),
        radial-gradient(circle at 85% 25%, rgba(14,165,233,0.18), transparent 30%),
        radial-gradient(circle at 50% 90%, rgba(168,85,247,0.15), transparent 35%),
        #070b17;
    color: #ffffff;
}

header {
    visibility: hidden;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* HERO */
.hero {
    text-align: center;
    padding: 45px 20px 30px;
}

.logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 75px;
    height: 75px;
    border-radius: 22px;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    font-size: 34px;
    box-shadow: 0 0 45px rgba(99,102,241,0.45);
    margin-bottom: 20px;
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 52px;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(90deg, #ffffff, #93c5fd, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #a7b0c5;
    font-size: 18px;
    max-width: 700px;
    margin: 14px auto;
}

/* STATUS */
.status {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 20px 0 35px;
}

.status-item {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    padding: 8px 16px;
    border-radius: 50px;
    color: #cbd5e1;
    font-size: 13px;
}

.green {
    color: #86efac;
}

/* CARDS */
.card {
    background: rgba(15,23,42,0.72);
    border: 1px solid rgba(148,163,184,0.14);
    border-radius: 24px;
    padding: 26px;
    margin-bottom: 22px;
    box-shadow: 0 20px 70px rgba(0,0,0,0.20);
    backdrop-filter: blur(20px);
}

.card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 21px;
    font-weight: 600;
    margin-bottom: 8px;
}

.card-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 18px;
}

/* BUTTONS */
.stButton > button {
    width: 100%;
    min-height: 52px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.12);
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white;
    font-weight: 700;
    font-size: 15px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 35px rgba(99,102,241,0.35);
}

/* TEXT AREA */
textarea {
    background: rgba(2,6,23,0.65) !important;
    color: #ffffff !important;
    border: 1px solid rgba(148,163,184,0.20) !important;
    border-radius: 15px !important;
}

/* AUDIO */
audio {
    width: 100%;
}

/* CHAT */
.user-msg {
    background: rgba(79,70,229,0.18);
    border: 1px solid rgba(99,102,241,0.25);
    padding: 18px;
    border-radius: 18px;
    margin: 12px 0;
}

.ai-msg {
    background: rgba(14,165,233,0.10);
    border: 1px solid rgba(14,165,233,0.20);
    padding: 18px;
    border-radius: 18px;
    margin: 12px 0;
}

.label {
    font-size: 12px;
    font-weight: 700;
    color: #93c5fd;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 7px;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #64748b;
    margin-top: 45px;
    font-size: 13px;
}

.feature {
    text-align: center;
    padding: 18px 10px;
}

.feature-icon {
    font-size: 28px;
}

.feature-title {
    font-weight: 700;
    margin-top: 8px;
}

.feature-text {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GROQ CLIENT
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "audio_response" not in st.session_state:
    st.session_state.audio_response = None

# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="logo">🎙️</div>

    <h1>VoiceFlow AI</h1>

    <p>
        Speak naturally. Think freely. Let AI understand your voice
        and respond with an intelligent voice conversation.
    </p>
</div>

<div class="status">
    <div class="status-item">🎤 Speech Recognition</div>
    <div class="status-item">🧠 Groq AI</div>
    <div class="status-item">🔊 Voice Response</div>
    <div class="status-item"><span class="green">●</span> Ready</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# API KEY WARNING
# ---------------------------------------------------------
if client is None:
    st.error(
        "Groq API key is not configured. Add GROQ_API_KEY to "
        ".streamlit/secrets.toml before using the application."
    )

# ---------------------------------------------------------
# MAIN COLUMNS
# ---------------------------------------------------------
left, right = st.columns([1, 1], gap="large")

# =========================================================
# LEFT SIDE - VOICE INPUT
# =========================================================
with left:

    st.markdown("""
    <div class="card">
        <div class="card-title">🎤 Voice Input</div>
        <div class="card-subtitle">
            Record your voice or upload an audio file.
        </div>
    </div>
    """, unsafe_allow_html=True)

    audio_value = st.audio_input(
        "Speak to VoiceFlow AI",
        key="voice_recorder"
    )

    uploaded_audio = st.file_uploader(
        "Or upload audio",
        type=["wav", "mp3", "m4a", "ogg", "webm"],
        label_visibility="collapsed"
    )

    audio_file = audio_value if audio_value is not None else uploaded_audio

    if audio_file is not None:

        st.audio(audio_file)

        st.markdown("<br>", unsafe_allow_html=True)

        process_button = st.button(
            "✨ Analyze Voice & Generate Response",
            use_container_width=True
        )

        if process_button:

            if client is None:
                st.error("Groq API key missing.")
            else:

                try:
                    # -----------------------------------------
                    # SPEECH TO TEXT
                    # -----------------------------------------
                    with st.spinner("🎧 Understanding your voice..."):

                        audio_bytes = audio_file.getvalue()

                        transcription = client.audio.transcriptions.create(
                            file=(
                                audio_file.name
                                if hasattr(audio_file, "name")
                                else "voice.wav",
                                audio_bytes
                            ),
                            model="whisper-large-v3-turbo",
                            response_format="json",
                            temperature=0
                        )

                        user_text = transcription.text.strip()

                    if not user_text:
                        st.warning("I could not understand the audio.")
                        st.stop()

                    # -----------------------------------------
                    # SAVE USER MESSAGE
                    # -----------------------------------------
                    st.session_state.messages.append({
                        "role": "user",
                        "text": user_text
                    })

                    # -----------------------------------------
                    # AI RESPONSE
                    # -----------------------------------------
                    with st.spinner("🧠 Generating AI response..."):

                        chat_messages = [
                            {
                                "role": "system",
                                "content": (
                                    "You are VoiceFlow AI, a friendly and "
                                    "professional voice assistant. "
                                    "Give natural, useful and concise answers. "
                                    "Avoid unnecessary long responses."
                                )
                            }
                        ]

                        # Add recent conversation history
                        for msg in st.session_state.messages[-6:]:
                            chat_messages.append({
                                "role": msg["role"],
                                "content": msg["text"]
                            })

                        completion = client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=chat_messages,
                            temperature=0.7,
                            max_tokens=500
                        )

                        ai_text = completion.choices[0].message.content.strip()

                    # -----------------------------------------
                    # SAVE AI RESPONSE
                    # -----------------------------------------
                    st.session_state.messages.append({
                        "role": "assistant",
                        "text": ai_text
                    })

                    # -----------------------------------------
                    # TEXT TO SPEECH
                    # -----------------------------------------
                    with st.spinner("🔊 Creating voice response..."):

                        # Groq Orpheus TTS has a 200-character
                        # input limit, so keep the spoken response short.
                        speech_text = ai_text[:200]

                        speech_response = client.audio.speech.create(
                            model="canopylabs/orpheus-v1-english",
                            voice="autumn",
                            input=speech_text,
                            response_format="wav"
                        )

                        audio_bytes = speech_response.read()

                        st.session_state.audio_response = audio_bytes

                    st.success("✅ Voice response generated successfully!")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# =========================================================
# RIGHT SIDE - AI RESPONSE
# =========================================================
with right:

    st.markdown("""
    <div class="card">
        <div class="card-title">🤖 AI Conversation</div>
        <div class="card-subtitle">
            Your voice conversation with the AI assistant.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.messages:

        for message in st.session_state.messages:

            if message["role"] == "user":

                st.markdown(f"""
                <div class="user-msg">
                    <div class="label">You said</div>
                    {message["text"]}
                </div>
                """, unsafe_allow_html=True)

            else:

                st.markdown(f"""
                <div class="ai-msg">
                    <div class="label">VoiceFlow AI</div>
                    {message["text"]}
                </div>
                """, unsafe_allow_html=True)

    else:

        st.markdown("""
        <div class="card" style="text-align:center; padding:50px 20px;">
            <div style="font-size:50px;">🎧</div>

            <div style="
                font-size:20px;
                font-weight:700;
                margin-top:15px;
            ">
                Start a Conversation
            </div>

            <div style="
                color:#94a3b8;
                margin-top:8px;
            ">
                Record your voice and let AI respond naturally.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# AUDIO RESPONSE
# ---------------------------------------------------------
if st.session_state.audio_response:

    st.markdown("""
    <div class="card">
        <div class="card-title">🔊 AI Voice Response</div>
        <div class="card-subtitle">
            Listen to the AI-generated response.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.audio(
        st.session_state.audio_response,
        format="audio/wav"
    )

    st.download_button(
        label="⬇️ Download AI Voice",
        data=st.session_state.audio_response,
        file_name="voiceflow_ai_response.wav",
        mime="audio/wav",
        use_container_width=True
    )

# ---------------------------------------------------------
# FEATURES
# ---------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div class="card">

<div style="
    text-align:center;
    font-family:'Space Grotesk';
    font-size:25px;
    font-weight:700;
    margin-bottom:25px;
">
    Powerful Voice AI
</div>

<div style="
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:20px;
">

<div class="feature">
    <div class="feature-icon">🎤</div>
    <div class="feature-title">Speech to Text</div>
    <div class="feature-text">
        Convert spoken words into accurate text.
    </div>
</div>

<div class="feature">
    <div class="feature-icon">🧠</div>
    <div class="feature-title">Groq Intelligence</div>
    <div class="feature-text">
        Get fast and natural AI-generated answers.
    </div>
</div>

<div class="feature">
    <div class="feature-icon">🔊</div>
    <div class="feature-title">Voice Response</div>
    <div class="feature-text">
        Hear the AI response as natural speech.
    </div>
</div>

</div>

</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CLEAR CHAT
# ---------------------------------------------------------
if st.session_state.messages:

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.audio_response = None
        st.rerun()

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("""
<div class="footer">
    VoiceFlow AI • Built with Python + Streamlit + Groq
    <br>
    Natural Voice • Fast AI • Modern Experience
</div>
""", unsafe_allow_html=True)
