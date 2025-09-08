import streamlit as st
import ollama
import base64

st.set_page_config(page_title="Multilingual Mental Health Chatbot")

LANGUAGES = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "ଓଡ଼ିଆ (Odia)": "or",
    "ಕನ್ನಡ (Kannada)": "kn",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "বাংলা (Bengali)": "bn"
}

def get_base64(background):
    with open(background, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

bin_str = get_base64("background.png")

st.markdown("""
    <style>
        .stApp {
            background-color: #000 !important;
            background-image: none !important;
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

def translate_text(text, target_lang):
    # Use model best supporting translation (like 5-translator on Ollama, or built-in translation via strong base models)
    response = ollama.chat(
        model="gemma:2b",
        messages=[{"role":"user", "content": f"Translate this to {target_lang}: {text}"}]
    )
    return response['message']['content']

def generate_response(user_input):
    # Translate to English if needed (for non-English models), send input to Ollama, get AI reply
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

for msg in st.session_state['conversation_history']:
    role = "You" if msg['role'] == "user" else "AI"
    st.markdown(f"**{role}:** {msg['content']}")

user_message = st.text_input(f"How can I help you today? (You can type in {lang})")

if user_message:
    with st.spinner("Thinking....."):
        ai_response = generate_response(user_message)
        st.markdown(f"**AI:** {ai_response}")

col1, col2 = st.columns(2)

with col1:
    if st.button("Give me a positive Affirmation"):
        affirmation = generate_affirmation()
        st.markdown(f"**Affirmation:** {affirmation}")

with col2:
    if st.button("Give me a guided meditation"):
        meditation_guide = generate_meditation_guide()
        st.markdown(f"**Guided Meditation:** {meditation_guide}")
