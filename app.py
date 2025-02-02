import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from datetime import datetime
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator, LANGUAGES
import time

# Must be the first Streamlit command
st.set_page_config(page_title="AI Teachers Hub", layout="wide")

# Define subjects dictionary at the top level
subjects = {
    "Data Science": "📊",
    "Machine Learning": "🤖",
    "Deep Learning": "🧠",
    "Artificial Intelligence": "🦾",
    "DBMS": "💾",
    "Statistics": "📈",
    "Python": "🐍",
    "R": "📉"
}

# Custom CSS for compact and futuristic UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');
    body {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Orbitron', sans-serif;
    }
    .main {
        padding: 1rem;
    }
    h1 {
        text-align: center;
        color: #58a6ff;
        text-shadow: 0px 0px 10px #58a6ff;
        font-size: 24px;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #4CAF50, #1E88E5);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.2);
        font-size: 14px;
    }
    .subject-card {
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #30363d;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        box-shadow: 0px 0px 15px rgba(255, 255, 255, 0.1);
        margin-bottom: 8px;
    }
    .chat-box {
        padding: 10px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-left: 5px solid #58a6ff;
        font-size: 14px;
    }
    .stTextArea>div>div>textarea {
        font-size: 14px;
        height: 80px !important;
    }
    .stSelectbox>div>div>div {
        font-size: 14px;
    }
    .stRadio>div {
        font-size: 14px;
    }
    .stSlider>div>div>div {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with structured history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for user query
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""

# Load environment variables
load_dotenv()

# Configure API key with error handling
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please set GEMINI_API_KEY in .env file")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
)

# Speech recognition function with live output
def recognize_speech(language_code="en-US"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            # Listen to the audio only once
            audio = recognizer.listen(source, timeout=5)
            result = recognizer.recognize_google(audio, language=language_code, show_all=True)
            
            if result and 'alternative' in result:
                # Extract the full recognized text
                full_text = result['alternative'][0]['transcript']
                
                # Simulate live output by displaying text in chunks
                text = ""
                words = full_text.split()  # Split the text into words
                for word in words:
                    text += word + " "
                    st.text(f"Recognized: {text}")
                    time.sleep(0.5)  # Add a small delay for the live effect
                
                return text.strip()
            else:
                st.error("No speech detected. Please try again.")
                return ""
        except sr.UnknownValueError:
            st.error("Could not understand audio. Please try again.")
            return ""
        except sr.RequestError:
            st.error("Speech recognition service is unavailable. Check your internet connection.")
            return ""
        except sr.WaitTimeoutError:
            st.error("No speech detected. Please speak again.")
            return ""

# Text-to-Speech function using gTTS
def speak_text(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3")
    # Delete the file after playing
    time.sleep(1)  # Ensure the file is played before deletion
    if os.path.exists("response.mp3"):
        os.remove("response.mp3")

# Translation function
def translate_text(text, target_language="en"):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text

# Main UI
st.markdown("<h1>🎓 AI Teachers Hub</h1>", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Language selection
    st.markdown("### 🌍 Choose Language")
    language_code = st.selectbox("Select Language", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x].capitalize(), index=list(LANGUAGES.keys()).index("en"))
    
    # Quick topics
    st.markdown("### 🎯 Quick Topics")
    topics = ["Algorithms", "Neural Networks", "Data Structures", "SQL"]
    selected_topic = st.radio("Select a topic:", topics)
    
    # Response size
    st.markdown("### 📏 Response Size")
    response_size = st.select_slider("Select answer length", options=["Brief", "Moderate", "Detailed"], value="Moderate")
    
    # Speech recording
    st.markdown("### 🎤 Speak Your Question")
    if st.button("🎙️ Start Recording"):
        st.session_state.user_query = recognize_speech(language_code=language_code)

# Main chat area
st.markdown("### 📚 Select Subject")
subject_choice = st.selectbox("", list(subjects.keys()), format_func=lambda x: f"{subjects[x]} {x}")

# User query input
st.session_state.user_query = st.text_area("", placeholder=f"Enter your {subject_choice} question here...", height=80, value=st.session_state.user_query)

# Get Answer button
if st.button("🚀 Get Answer"):
    if st.session_state.user_query.strip():
        with st.spinner(f'🤔 {subject_choice} teacher is thinking...'):
            # Modify the prompt based on response_size
            if response_size == "Brief":
                prompt = f"Provide a brief answer to the following question: {st.session_state.user_query}"
            elif response_size == "Moderate":
                prompt = f"Provide a moderate-length answer to the following question: {st.session_state.user_query}"
            elif response_size == "Detailed":
                prompt = f"Provide a detailed and comprehensive answer to the following question: {st.session_state.user_query}"
            
            # Generate the response using the modified prompt
            response = model.generate_content(prompt).text
            
            # Translate the response
            translated_response = translate_text(response, target_language=language_code)
            
            # Display the answer
            st.markdown("### 📝 Answer")
            st.markdown(f"<div class='chat-box'>{translated_response}</div>", unsafe_allow_html=True)
            
            # Add to chat history
            st.session_state.chat_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "subject": subject_choice,
                "topic": selected_topic,
                "response_size": response_size,
                "question": st.session_state.user_query,
                "answer": translated_response
            })
            
            # Play the audio response
            st.markdown("### 🔊 Listen to Answer")
            speak_text(translated_response, lang=language_code)
    else:
        st.warning("⚠️ Please enter or speak a question!")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center'><p>Made with ❤️ for students everywhere</p></div>", unsafe_allow_html=True)