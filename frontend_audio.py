import streamlit as st
import requests
from dotenv import load_dotenv
import os
import base64

load_dotenv()

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
enable_tts = st.checkbox("Enable Text-to-Speech", value=True)
selected_voice = st.selectbox("Select TTS voice:", voices, disabled=not enable_tts)

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
        with st.spinner("Getting response from agent..."):
            # Define request payload
            request = {
                "model_name": selected_model,
                "model_provider": provider,
                "messages": [user_query],
                "system_prompt": system_prompt,
                "allow_search": allow_web_search,
                "tts_enabled": enable_tts,
                "voice_name": selected_voice if enable_tts else None
            }
            
            # Get response
            response = requests.post(API_URL, json=request)
            
            if response.status_code == 200:
                
                response_data = response.json()
                
                if "error" in response_data:
                    st.error(response_data["error"])
                else:
                    # Store the response in session state for replay
                    if "text" in response_data:
                        # New response format with separate text and audio
                        text_response = response_data["text"]
                        audio_base64 = response_data.get("audio")
                        
                        # Display the text response
                        st.subheader("Agent Response")
                        st.markdown(text_response)
                        
                        # Play audio if available
                        if audio_base64:
                            st.session_state['last_audio'] = audio_base64
                            st.audio(f"data:audio/mp3;base64,{audio_base64}", format="audio/mp3")
                    else:
                        # Old response format (just text)
                        st.subheader("Agent Response")
                        st.markdown(response_data)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
    else:
        st.warning("Please enter a query first.")

# Add a button to play the last response again if available
if 'last_audio' in st.session_state and st.session_state['last_audio'] and st.button("Play Last Response Again"):
    st.audio(f"data:audio/mp3;base64,{st.session_state['last_audio']}", format="audio/mp3")