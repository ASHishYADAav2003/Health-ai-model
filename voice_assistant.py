import streamlit as st
import ollama
import base64
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO


st.set_page_config(page_title="Multilingual Mental Health Chatbot")

LANGUAGES = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "ଓଡ଼ିଆ (Odia)": "or",
    "ಕನ್ನಡ (Kannada)": "kn",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "বাংলা (Bengali)": "bn"
}

LANG_CODES_TTS = {
    "English": "en",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "বাংলা (Bengali)": "bn",
    "ಕನ್ನಡ (Kannada)": "kn",
    "ଓଡ଼ିଆ (Odia)": "or",
    "हिन्दी (Hindi)": "hi"
}

LANG_CODES_SR = {
    "English": "en-IN",
    "ਪੰਜਾਬੀ (Punjabi)": "pa-IN",
    "বাংলা (Bengali)": "bn-IN",
    "ಕನ್ನಡ (Kannada)": "kn-IN",
    "ଓଡ଼ିଆ (Odia)": "or-IN",
    "हिन्दी (Hindi)": "hi-IN"
}

# Black background CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #000 !important;
            background-image: none !important;
            color: white;
        }
        .stTextInput, .stSelectbox, .stButton > button {
            color: black !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.session_state.setdefault('conversation_history', [])
st.session_state.setdefault('selected_lang', "English")

st.title("Mental Health Support Agent")

# Language selection
lang = st.selectbox("Choose your language:", list(LANGUAGES.keys()))
st.session_state['selected_lang'] = lang
lang_code = LANGUAGES[lang]

# Speech recognition helper
def transcribe_audio(audio_file, language_code):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=language_code)
        return text
    except Exception as e:
        return f"Could not recognize audio: {e}"

# Text-to-speech helper
def speak_text(text, language_code):
    tts = gTTS(text=text, lang=language_code)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

def translate_text(text, target_lang):
    response = ollama.chat(
        model="gemma:2b",
        messages=[{"role":"user", "content": f"Translate this to {target_lang}: {text}"}]
    )
    return response['message']['content']

def generate_response(user_input):
    input_prompt = user_input
    if lang_code != "en":
        input_prompt = f"Reply in {lang} language: {user_input}"
    st.session_state['conversation_history'].append({"role":"user", "content": input_prompt})
    response = ollama.chat(model="gemma:2b", messages=st.session_state['conversation_history'])
    ai_response = response['message']['content']
    st.session_state['conversation_history'].append({"role":"assistant", "content": ai_response})
    return ai_response

def generate_affirmation():
    prompt = f"Provide a positive affirmation in {lang} language to encourage someone who is feeling stressed or overwhelmed."
    response = ollama.chat(model="gemma:2b", messages=[{"role":"user","content":prompt}])
    return response['message']['content']

def generate_meditation_guide():
    prompt = f"Provide a 5-minute guided meditation script in {lang} language to help someone relax and reduce stress."
    response = ollama.chat(model="gemma:2b", messages=[{"role":"user","content":prompt}])
    return response['message']['content']

# Display conversation history
for msg in st.session_state['conversation_history']:
    role = "You" if msg['role'] == "user" else "AI"
    st.markdown(f"**{role}:** {msg['content']}")

# Voice input via uploaded audio file
uploaded_audio = st.file_uploader("🎤 Upload or record voice (WAV/MP3)", type=["wav", "mp3"])
if uploaded_audio is not None:
    lang_code_sr = LANG_CODES_SR.get(lang, "en-IN")
    input_text = transcribe_audio(uploaded_audio, lang_code_sr)
    st.markdown(f"**Recognized text:** {input_text}")
    if not input_text.startswith("Could not recognize"):
        ai_response = generate_response(input_text)
        st.markdown(f"**AI:** {ai_response}")
        # Voice output of response
        lang_code_tts = LANG_CODES_TTS.get(lang, "en")
        mp3_fp = speak_text(ai_response, lang_code_tts)
        st.audio(mp3_fp, format="audio/mp3")

# Text input fallback
user_message = st.text_input(f"How can I help you today? (You can type in {lang})")
if user_message:
    with st.spinner("Thinking....."):
        ai_response = generate_response(user_message)
        st.markdown(f"**AI:** {ai_response}")
        # Voice output of response
        lang_code_tts = LANG_CODES_TTS.get(lang, "en")
        mp3_fp = speak_text(ai_response, lang_code_tts)
        st.audio(mp3_fp, format="audio/mp3")

col1, col2 = st.columns(2)

with col1:
    if st.button("Give me a positive Affirmation"):
        affirmation = generate_affirmation()
        st.markdown(f"**Affirmation:** {affirmation}")
        # Voice output
        lang_code_tts = LANG_CODES_TTS.get(lang, "en")
        mp3_fp = speak_text(affirmation, lang_code_tts)
        st.audio(mp3_fp, format="audio/mp3")

with col2:
    if st.button("Give me a guided meditation"):
        meditation = generate_meditation_guide()
        st.markdown(f"**Guided Meditation:** {meditation}")
        # Voice output
        lang_code_tts = LANG_CODES_TTS.get(lang, "en")
        mp3_fp = speak_text(meditation, lang_code_tts)
        st.audio(mp3_fp, format="audio/mp3")
