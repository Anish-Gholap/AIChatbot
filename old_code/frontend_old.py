import streamlit as st
import requests
import azure.cognitiveservices.speech as speech
from jigsawstack import JigsawStack
from dotenv import load_dotenv
import os
import base64
import tempfile

load_dotenv()

# Add this to clean up temp files when the app restarts
if 'temp_files' in st.session_state:
    for file in st.session_state['temp_files']:
        try:
            os.unlink(file)
        except:
            pass  # Ignore errors during cleanup
    st.session_state['temp_files'] = []

# Function to generate speech from text using JigsawStack
def text_to_speech_jigsawstack(text, voice_name):
    try:
        # Initialize the JigsawStack client
        jigsaw = JigsawStack(api_key=JIGSAWSTACK_API_KEY)
        
        with st.spinner("Generating audio..."):
            # Use the client to generate speech
            response = jigsaw.audio.text_to_speech({
                "text": text,
                "accent": voice_name
            })
            
            audio_content = response.content
            
            # Create a temporary file with delete=False
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_filename = temp_file.name
            temp_file.close()  # Close the file before writing to it
            
            try:
                # Write the audio content to the file
                with open(temp_filename, "wb") as f:
                    f.write(audio_content)
                
                # Read the audio file and encode it to base64
                with open(temp_filename, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                # Don't delete the file immediately - store it for later cleanup
                if 'temp_files' not in st.session_state:
                    st.session_state['temp_files'] = []
                
                st.session_state['temp_files'].append(temp_filename)
                
                # Clean up old files (keep only the 5 most recent)
                if len(st.session_state['temp_files']) > 5:
                    old_files = st.session_state['temp_files'][:-5]
                    st.session_state['temp_files'] = st.session_state['temp_files'][-5:]
                    
                    for old_file in old_files:
                        try:
                            os.unlink(old_file)
                        except:
                            pass  # Ignore errors during cleanup of old files
                
                return audio_base64
                
            except Exception as e:
                st.error(f"Error processing audio file: {str(e)}")
                return None
                
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        st.write(f"Error details: {str(e)}")
        return None

# Set up keys for azure speech
JIGSAWSTACK_API_KEY = os.getenv("JIGSAWSTACK_API_KEY")

# Available voices for TTS
voices = [
    "en-SG-female-1",
    "en-SG-male-1"
]

# Setup the frontend using streamlit
st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("AI ChatBot Agent")
st.write("Create and Interact with AI Agents")

# Get User input
# Text box for system prompt
system_prompt = st.text_area("Define your AI Agent: ", height=70, placeholder="Type your system prompt here...")

# Radio buttons to select model provider
MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "deepseek-r1-distill-qwen-32b", "gemma2-9b-it"]
MODEL_NAMES_OPENAI = ['gpt-4o']

provider = st.radio("Select Provider:", ("Groq", "OpenAI"))

# Select tts
selected_voice = st.selectbox("Select TTS voice:", voices)

if provider == "Groq":
    selected_model = st.selectbox("Select Groq Model:", MODEL_NAMES_GROQ)
else:
    selected_model = st.selectbox("Select OpenAI Model:", MODEL_NAMES_OPENAI)

# Checkbox for web search
allow_web_search = st.checkbox("Allow Web Search")

# Text box for user query
user_query = st.text_area("Enter your query: ", height=150, placeholder="Ask Anything!")

# BACKEND ENDPOINT URL
API_URL = "http://127.0.0.1:3000/chat"

# Submit button to send request
if st.button("Ask Agent"):
    
    # Check if user typed in query
    if user_query.strip():
        
        # Define request payload
        request = {
            "model_name": selected_model,
            "model_provider": provider,
            "messages": [user_query],
            "system_prompt": system_prompt,
            "allow_search": allow_web_search
        }
        
        # Get response
        response = requests.post(API_URL, json=request)
        
        if response.status_code == 200:
            
            response_data = response.json()
            
            if "error" in response_data:
                
                st.error(response_data["error"])
                
            else:
                
                # Get response and display it
                st.subheader("Agent Response")
                st.markdown(f"Final Response: {response_data}")
                
                # Generate TTS
                audio_base64 = text_to_speech_jigsawstack(response_data, selected_voice)
                
                if audio_base64:
                    # Display audio player
                    st.audio(f"data:audio/mp3;base64,{audio_base64}", format="audio/mp3")

# Add a button to play the last response again if available
if 'last_audio' not in st.session_state:
    st.session_state['last_audio'] = None

if st.session_state.get('last_audio') and st.button("Play Last Response Again"):
    st.audio(f"data:audio/mp3;base64,{st.session_state['last_audio']}", format="audio/mp3")