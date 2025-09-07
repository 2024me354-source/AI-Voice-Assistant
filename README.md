🎙️ Voice AI Assistant

An interactive voice-enabled AI assistant built with Streamlit and powered by Groq AI.
This app lets you speak, upload audio, or type messages to chat with the assistant and optionally get AI responses in text and speech.

🚀 Features

🎤 Record Voice directly in the browser.

📁 Upload audio files (.wav, .mp3, .m4a).

⌨️ Type text messages for instant AI responses.

🤖 Powered by Groq AI for fast & intelligent responses.

🔊 Text-to-Speech (TTS) responses when available.

✨ Beautiful custom UI with animations and styling.

🗑️ Clear conversation history easily.

🛠️ Tech Stack

Streamlit
 – Web app framework

Groq API
 – AI inference & TTS/ASR models

Whisper Large V3 Turbo
 – Speech-to-Text

DeepSeek-R1 Distill LLaMA-70B – Conversational AI model

PlayAI TTS – Text-to-Speech voices

pydub – Audio handling

⚙️ Setup
1️⃣ Clone the repo
git clone https://github.com/your-username/voice-ai-assistant.git
cd voice-ai-assistant

2️⃣ Install dependencies
pip install -r requirements.txt


(Make sure you have ffmpeg installed for audio processing with pydub.)

3️⃣ Add API Key

Get your Groq API Key from Groq Console
 and set it:

Windows (PowerShell)
setx GROQ_API_KEY 

4️⃣ Run the app
streamlit run app.py

🎯 Usage

Choose a tab:

🎤 Record your voice

📁 Upload an audio file

⌨️ Type a text message

The assistant will:

Transcribe your voice (if applicable)

Generate an intelligent AI response

Optionally speak the answer back (TTS)

View and listen to responses in real time.

📸 Demo UI

Gradient background with floating header

Interactive tabs for input methods

AI responses displayed in styled cards

Audio playback for generated speech

🧹 Clearing Conversation

Click 🗑️ Clear Conversation to reset chat history and audio files.

⚠️ Notes

TTS is rate-limited. If limits are reached, the app switches to text-only mode automatically.

Requires Groq API access.

📜 License

MIT License © 2025 Abdullah Naveed
