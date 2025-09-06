import os
import tempfile
from pathlib import Path
import streamlit as st
import requests
from pydub import AudioSegment
import uuid
import json
import base64

# ✅ Check API key
if not os.environ.get("GROQ_API_KEY"):
    st.error("❌ GROQ_API_KEY not found! Please add it in Hugging Face → Settings → Secrets.")
    st.stop()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_BASE = "https://api.groq.com/openai/v1"

# Custom CSS for unique styling
def inject_custom_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
    }
    
    /* Header styling - FIXED TEXT COLOR */
    .header {
        text-align: center;
        color: #333333 !important; /* Changed from white to dark gray */
        padding: 20px;
        background: rgba(255, 255, 255, 0.9); /* More opaque background */
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: white;
        font-weight: bold;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.4) !important;
        color: #764ba2 !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 15px;
        border: 2px solid #667eea;
        padding: 15px;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Audio player styling */
    audio {
        width: 100%;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Card styling for responses - FIXED TEXT COLOR */
    .response-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        color: #333333 !important; /* Dark text for readability */
    }
    
    /* Ensure text inside cards is visible */
    .response-card h4,
    .response-card p {
        color: #333333 !important;
    }
    
    /* Footer styling - FIXED TEXT COLOR */
    .footer {
        text-align: center;
        color: white !important;
        opacity: 0.9;
        margin-top: 30px;
        padding: 15px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }
    
    /* Animation for processing */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
         100% { opacity: 1; }
    }
    
    .processing {
        animation: pulse 2s infinite;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    /* Floating animation */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)

# Custom JavaScript for interactive effects
def inject_custom_js():
    st.markdown("""
    <script>
    // Add floating animation to elements
    document.addEventListener('DOMContentLoaded', function() {
        // Add floating effect to header
        const header = document.querySelector('.header');
        if (header) {
            header.classList.add('floating');
        }
        
        // Add click effects to buttons
        const buttons = document.querySelectorAll('.stButton button');
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });
        });
        
        // Smooth scrolling for better UX
        const smoothScroll = function(element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        };
    });
    
    // Typing animation for responses
    function typeWriter(element, text, speed = 50) {
        let i = 0;
        element.innerHTML = '';
        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        type();
    }
    </script>
    """, unsafe_allow_html=True)

# Custom HTML header with animated elements - FIXED TEXT COLOR
def create_custom_header():
    st.markdown("""
    <div class="header">
        <h1 style="margin:0; font-size:2.5em; color: #333333 !important;">🎙️ Voice AI Assistant</h1>
        <p style="margin:0; opacity:0.8; color: #333333 !important;">Powered by Groq AI • Speak, Upload, or Type</p>
        <div style="margin-top:10px;">
            <span style="font-size:2em; color: #333333 !important;">⚡</span>
            <span style="font-size:1.5em; margin:0 10px; color: #333333 !important;">🤖</span>
            <span style="font-size:2em; color: #333333 !important;">🎯</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def groq_api_request(endpoint, method="POST", json_data=None, files=None):
    """Make direct API requests to Groq API"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        url = f"{GROQ_API_BASE}/{endpoint}"
        
        if method == "POST":
            if files:
                response = requests.post(url, headers=headers, files=files, data=json_data)
            else:
                response = requests.post(url, headers=headers, json=json_data)
        else:
            response = requests.get(url, headers=headers, params=json_data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            error_data = e.response.json()
            st.warning(f"⚠️ Rate limit exceeded: {error_data.get('error', {}).get('message', 'Unknown error')}")
            return {"error": "rate_limit_exceeded"}
        else:
            st.error(f"API request failed: {e}")
            return None
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None

# Initialize session state
if 'user_text' not in st.session_state:
    st.session_state.user_text = None
if 'ai_text' not in st.session_state:
    st.session_state.ai_text = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'audio_files' not in st.session_state:
    st.session_state.audio_files = []
if 'clear_convo' not in st.session_state:
    st.session_state.clear_convo = False
if 'tts_available' not in st.session_state:
    st.session_state.tts_available = True

def process_text_input(user_text):
    """Process text input and generate response"""
    try:
        response = groq_api_request("chat/completions", json_data={
            "model": "deepseek-r1-distill-llama-70b",
            "messages": [{"role": "user", "content": user_text}],
            "temperature": 0.6,
            "max_tokens": 1024,
            "top_p": 0.95
        })
        
        if not response or "error" in response:
            return None, None
            
        ai_text = response["choices"][0]["message"]["content"]
        
        audio_path = None
        if st.session_state.tts_available:
            try:
                tts_response = groq_api_request("audio/speech", json_data={
                    "model": "playai-tts",
                    "voice": "Aaliyah-PlayAI",
                    "response_format": "wav",
                    "input": ai_text[:500],
                })
                
                if tts_response and "error" in tts_response and tts_response["error"] == "rate_limit_exceeded":
                    st.session_state.tts_available = False
                    st.warning("🎙️ TTS rate limit reached. Text-only mode activated.")
            except Exception as e:
                if "rate_limit_exceeded" in str(e) or "Rate limit" in str(e) or "429" in str(e):
                    st.session_state.tts_available = False
        
        return ai_text, audio_path

    except Exception as e:
        st.error(f"⚠️ Error processing text: {e}")
        return None, None

def process_audio_input(audio_file_path):
    """Process audio input and generate response"""
    try:
        with open(audio_file_path, "rb") as file:
            files = {
                "file": (os.path.basename(audio_file_path), file.read(), "audio/wav")
            }
            data = {
                "model": "whisper-large-v3-turbo",
                "response_format": "verbose_json"
            }
            
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            
            response = requests.post(
                f"{GROQ_API_BASE}/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )
            
            response.raise_for_status()
            transcription = response.json()
            
        user_text = transcription["text"]

        chat_response = groq_api_request("chat/completions", json_data={
            "model": "deepseek-r1-distill-llama-70b",
            "messages": [{"role": "user", "content": user_text}],
            "temperature": 0.6,
            "max_tokens": 1024,
            "top_p": 0.95
        })
        
        if not chat_response or "error" in chat_response:
            return user_text, "Error: API request failed", None
            
        ai_text = chat_response["choices"][0]["message"]["content"]
        
        audio_path = None
        if st.session_state.tts_available:
            try:
                tts_response = groq_api_request("audio/speech", json_data={
                    "model": "playai-tts",
                    "voice": "Aaliyah-PlayAI",
                    "response_format": "wav",
                    "input": ai_text[:500],
                })
                
                if tts_response and "error" in tts_response and tts_response["error"] == "rate_limit_exceeded":
                    st.session_state.tts_available = False
            except Exception as e:
                if "rate_limit_exceeded" in str(e) or "Rate limit" in str(e) or "429" in str(e):
                    st.session_state.tts_available = False
        
        return user_text, ai_text, audio_path

    except Exception as e:
        if "rate_limit_exceeded" in str(e) or "Rate limit" in str(e) or "429" in str(e):
            st.warning("⚠️ Rate limit exceeded. Text-only mode activated.")
            return user_text, ai_text if 'ai_text' in locals() else "Error", None
        else:
            st.error(f"⚠️ Error during processing: {e}")
            return None, None, None

def clear_conversation():
    """Clear the conversation and clean up files"""
    for audio_file in st.session_state.audio_files:
        try:
            if os.path.exists(audio_file):
                os.unlink(audio_file)
        except:
            pass
    
    st.session_state.user_text = None
    st.session_state.ai_text = None
    st.session_state.audio_path = None
    st.session_state.audio_files = []
    st.session_state.clear_convo = True
    st.session_state.tts_available = True

# 🔹 Streamlit UI with Custom Styling
st.set_page_config(
    page_title="Voice AI Assistant", 
    page_icon="🎙️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS and JS
inject_custom_css()
inject_custom_js()
create_custom_header()

# Main content with gradient background
st.markdown('<div class="main">', unsafe_allow_html=True)

if not st.session_state.tts_available:
    st.warning("🎙️ TTS Rate Limit Reached: Audio responses temporarily unavailable.")
else:
    st.info("💡 Pro Tip: Try speaking naturally for best results!")

if st.session_state.clear_convo:
    st.session_state.clear_convo = False
    st.rerun()

# Create tabs with custom styling
tab1, tab2, tab3 = st.tabs(["🎤 Record Voice", "📁 Upload Audio", "⌨️ Type Message"])

with tab1:
    st.markdown("### Speak your mind...")
    recorded_audio = st.audio_input("Click to record", key="record")
    if recorded_audio:
        audio_bytes = recorded_audio.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        with st.spinner("🎵 Processing your voice..."):
            user_text, ai_text, audio_path = process_audio_input(tmp_path)
            
            st.session_state.user_text = user_text
            st.session_state.ai_text = ai_text
            st.session_state.audio_path = audio_path
            if audio_path:
                st.session_state.audio_files.append(audio_path)
            
            try:
                os.unlink(tmp_path)
            except:
                pass

with tab2:
    st.markdown("### Upload an audio file")
    uploaded_file = st.file_uploader("Choose audio file", type=["wav", "mp3", "m4a"], key="upload")
    if uploaded_file:
        file_bytes = uploaded_file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name

        with st.spinner("📂 Processing your file..."):
            user_text, ai_text, audio_path = process_audio_input(tmp_path)
            
            st.session_state.user_text = user_text
            st.session_state.ai_text = ai_text
            st.session_state.audio_path = audio_path
            if audio_path:
                st.session_state.audio_files.append(audio_path)
            
            try:
                os.unlink(tmp_path)
            except:
                pass

with tab3:
    st.markdown("### Type your message")
    text_input = st.text_area("Enter your text here:", height=120, key="text", 
                            placeholder="Type your message here...")
    text_submit = st.button("🚀 Send Message", key="text_btn", use_container_width=True)
    if text_input and text_submit:
        with st.spinner("💭 Generating response..."):
            ai_text, audio_path = process_text_input(text_input)
            
            st.session_state.user_text = text_input
            st.session_state.ai_text = ai_text
            st.session_state.audio_path = audio_path
            if audio_path:
                st.session_state.audio_files.append(audio_path)

# Display results with custom styling
if st.session_state.user_text and st.session_state.ai_text:
    st.markdown("---")
    st.markdown("### 📋 Conversation Results")
    
    # Your input card - FIXED TEXT COLOR
    st.markdown("""
    <div class="response-card">
        <h4 style="color: #667eea; margin:0;">🎤 Your Input</h4>
        <p style="margin:10px 0 0 0; line-height:1.6; color: #333333 !important;">""" + st.session_state.user_text + """</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI response card - FIXED TEXT COLOR
    st.markdown("""
    <div class="response-card">
        <h4 style="color: #764ba2; margin:0;">🤖 AI Response</h4>
        <p style="margin:10px 0 0 0; line-height:1.6; color: #333333 !important;">""" + st.session_state.ai_text + """</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Audio response
    if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
        st.markdown("""
        <div class="response-card">
            <h4 style="color: #FF6B6B; margin:0;">🔊 Audio Response</h4>
        </div>
        """, unsafe_allow_html=True)
        st.audio(st.session_state.audio_path, format="audio/wav")
    elif not st.session_state.tts_available:
        st.info("🔇 Audio responses temporarily unavailable due to rate limits")
    
    # Clear button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        clear_conversation()
        st.rerun()

# Footer - FIXED TEXT COLOR
st.markdown("---")
st.markdown("""
<div class="footer">
    <p style="margin:5px 0; color: white !important; font-weight: bold;">Powered by Groq AI • Built with Streamlit</p>
    <p style="margin:5px 0; color: white !important;">⚡ Fast • 🤖 Intelligent • 🎯 Accurate</p>
</div>
""", unsafe_allow_html=True)

# Close main div
st.markdown('</div>', unsafe_allow_html=True)
