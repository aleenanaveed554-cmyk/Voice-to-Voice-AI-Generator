import os
import tempfile
import streamlit as st
from groq import Groq

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Voxora AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(124,58,237,0.25), transparent 30%),
        radial-gradient(circle at 85% 25%, rgba(59,130,246,0.20), transparent 30%),
        radial-gradient(circle at 50% 90%, rgba(236,72,153,0.12), transparent 35%),
        #070b18;
    color: white;
}

/* Remove default top space */
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

/* Main heading */
.hero {
    text-align: center;
    padding: 35px 20px 20px 20px;
}

.logo {
    width: 78px;
    height: 78px;
    margin: auto;
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 38px;

    background: linear-gradient(
        135deg,
        rgba(139,92,246,0.35),
        rgba(59,130,246,0.30)
    );

    border: 1px solid rgba(255,255,255,0.15);

    box-shadow:
        0 0 40px rgba(139,92,246,0.35);
}

.hero h1 {
    font-size: 52px;
    font-weight: 800;
    margin: 18px 0 8px 0;

    background: linear-gradient(
        90deg,
        #ffffff,
        #c4b5fd,
        #93c5fd
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #aab4cc;
    font-size: 18px;
    margin: 0 auto;
    max-width: 650px;
}

/* Glass cards */
.glass {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 24px;
    padding: 28px;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 70px rgba(0,0,0,0.20);
}

.card-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.card-subtitle {
    color: #8f9ab3;
    font-size: 14px;
    margin-bottom: 20px;
}

/* Voice circle */
.voice-circle {
    width: 120px;
    height: 120px;
    margin: 15px auto 25px auto;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 48px;

    background:
        radial-gradient(
            circle,
            rgba(139,92,246,0.35),
            rgba(59,130,246,0.12)
        );

    border: 1px solid rgba(167,139,250,0.35);

    box-shadow:
        0 0 0 12px rgba(139,92,246,0.04),
        0 0 60px rgba(139,92,246,0.30);
}

/* Buttons */
.stButton > button {
    width: 100%;
    border: none;
    border-radius: 14px;
    min-height: 48px;

    font-weight: 700;
    font-size: 15px;

    color: white;

    background: linear-gradient(
        90deg,
        #7c3aed,
        #2563eb
    );

    box-shadow:
        0 10px 30px rgba(99,102,241,0.25);

    transition: 0.2s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow:
        0 15px 35px rgba(99,102,241,0.40);
}

/* Audio */
audio {
    width: 100%;
}

/* Text area */
textarea {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
    border-radius: 15px !important;
}

/* Status */
.status {
    text-align: center;
    color: #9ca3af;
    font-size: 13px;
    margin-top: 10px;
}

/* Feature cards */
.feature {
    text-align: center;
    padding: 20px;
    border-radius: 18px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
}

.feature-icon {
    font-size: 28px;
}

.feature-title {
    font-weight: 700;
    margin-top: 8px;
}

.feature-text {
    color: #8f9ab3;
    font-size: 13px;
}

/* Hide Streamlit menu/footer */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# API KEY
# =========================================================

api_key = None

try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY nahi mili.")
    st.info("Streamlit Secrets mein GROQ_API_KEY add karein.")
    st.stop()

client = Groq(api_key=api_key)

# =========================================================
# SESSION STATE
# =========================================================

if "conversation" not in st.session_state:
    st.session_state.conversation = []

# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero">

    <div class="logo">🎙️</div>

    <h1>Voxora AI</h1>

    <p>
        Voice to Voice AI Generator
        <br>
        <span style="font-size:15px;">
        Speak naturally. Think intelligently. Talk with AI.
        </span>
    </p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# FEATURES
# =========================================================

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🎤</div>
        <div class="feature-title">Voice Input</div>
        <div class="feature-text">
        Speak naturally with your AI
        </div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🧠</div>
        <div class="feature-title">Smart AI</div>
        <div class="feature-text">
        Intelligent real-time responses
        </div>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🔊</div>
        <div class="feature-title">Voice Output</div>
        <div class="feature-text">
        Listen to AI responses
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# MAIN COLUMNS
# =========================================================

left, right = st.columns(2, gap="large")

# =========================================================
# LEFT - VOICE INPUT
# =========================================================

with left:

    st.markdown("""
    <div class="glass">

        <div class="card-title">
            🎤 Talk to Voxora
        </div>

        <div class="card-subtitle">
            Record your voice and let AI understand you.
        </div>

        <div class="voice-circle">
            🎙️
        </div>

    </div>
    """, unsafe_allow_html=True)

    audio = st.audio_input(
        "🎙️ Tap here to record your voice"
    )

# =========================================================
# RIGHT - AI RESPONSE
# =========================================================

with right:

    st.markdown("""
    <div class="glass">

        <div class="card-title">
            🤖 AI Conversation
        </div>

        <div class="card-subtitle">
            Your AI response will appear here.
        </div>

    """, unsafe_allow_html=True)

    if st.session_state.conversation:

        for msg in st.session_state.conversation[-4:]:

            if msg["role"] == "user":

                st.markdown(
                    f"""
                    <div style="
                    background:rgba(59,130,246,0.10);
                    border-radius:14px;
                    padding:13px;
                    margin-bottom:10px;">
                    <b>🗣️ You</b><br>
                    {msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                    background:rgba(139,92,246,0.10);
                    border-radius:14px;
                    padding:13px;
                    margin-bottom:10px;">
                    <b>🤖 Voxora</b><br>
                    {msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:

        st.markdown("""
        <div style="
        text-align:center;
        padding:35px 10px;
        color:#77829b;">

        🎧<br><br>
        Start a voice conversation<br>
        and your AI response will appear here.

        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# PROCESS AUDIO
# =========================================================

if audio is not None:

    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner("🎧 Listening to your voice..."):

        try:

            # -----------------------------------------------
            # SAVE AUDIO
            # -----------------------------------------------

            audio_bytes = audio.getvalue()

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav"
            ) as temp_file:

                temp_file.write(audio_bytes)
                audio_path = temp_file.name

            # -----------------------------------------------
            # SPEECH TO TEXT
            # -----------------------------------------------

            with open(audio_path, "rb") as audio_file:

                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    response_format="text"
                )

            user_text = str(transcription).strip()

            if not user_text:
                st.warning("Voice samajh nahi aayi. Dobara try karein.")
                st.stop()

            # -----------------------------------------------
            # SHOW USER TEXT
            # -----------------------------------------------

            st.markdown("### 🗣️ You said")

            st.markdown(
                f"""
                <div class="glass">
                    {user_text}
                </div>
                """,
                unsafe_allow_html=True
            )

            # -----------------------------------------------
            # ADD USER MESSAGE
            # -----------------------------------------------

            st.session_state.conversation.append({
                "role": "user",
                "content": user_text
            })

            # -----------------------------------------------
            # AI RESPONSE
            # -----------------------------------------------

            with st.spinner("🧠 Voxora is thinking..."):

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are Voxora AI, a friendly voice-to-voice assistant.

Answer naturally like a real person.
Keep responses clear and conversational.
Do not use unnecessary headings.
Do not make responses extremely long.
"""
                        }
                    ] + st.session_state.conversation,
                    temperature=0.7,
                    max_tokens=400
                )

            ai_response = response.choices[0].message.content.strip()

            # -----------------------------------------------
            # SAVE RESPONSE
            # -----------------------------------------------

            st.session_state.conversation.append({
                "role": "assistant",
                "content": ai_response
            })

            # -----------------------------------------------
            # SHOW AI RESPONSE
            # -----------------------------------------------

            st.markdown("### 🤖 Voxora AI")

            st.markdown(
                f"""
                <div class="glass">
                    <div style="
                    font-size:17px;
                    line-height:1.8;">
                    {ai_response}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # -----------------------------------------------
            # TEXT TO SPEECH
            # -----------------------------------------------

            with st.spinner("🔊 Creating AI voice..."):

                speech = client.audio.speech.create(
                    model="canopylabs/orpheus-v1-english",
                    voice="tara",
                    input=ai_response,
                    response_format="wav"
                )

                voice_data = speech.read()

            # -----------------------------------------------
            # PLAY VOICE
            # -----------------------------------------------

            st.markdown("### 🔊 AI Voice")

            st.audio(
                voice_data,
                format="audio/wav"
            )

            st.download_button(
                label="⬇️ Download AI Voice",
                data=voice_data,
                file_name="voxora_ai_response.wav",
                mime="audio/wav"
            )

        except Exception as error:

            st.error("❌ Something went wrong.")

            st.code(str(error))

# =========================================================
# FOOTER
# =========================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="
text-align:center;
color:#69748c;
font-size:13px;
padding:20px;">

🎙️ <b>Voxora AI</b><br>
Voice to Voice • Powered by Groq

</div>
""", unsafe_allow_html=True)
