import os
import requests
import streamlit as st


# Setup the frontend using streamlit
st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("AI ChatBot Agent")
st.write("Create and Interact with AI Agents")

# Text box for system prompt
system_prompt = st.text_area("Define your AI Agent: ", height=70, placeholder="Type your system prompt here...")

# Radio buttons to select model provider
MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "deepseek-r1-distill-qwen-32b", "gemma2-9b-it"]
MODEL_NAMES_OPENAI = ['gpt-4o']

provider = st.radio("Select Provider:", ("Groq", "OpenAI"))

# Available voices for TTS
voices = [
    "en-SG-female-1",
    "en-SG-male-1"
]

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
            "allow_search": allow_web_search,
            "tts_enabled": True,
            "voice": selected_voice
        }
        
        response = requests.post(API_URL, json=request)

        if response.status_code == 200:
            # Success case - normal flow
            response_data = response.json()
            
            # Display the text response
            st.subheader("Agent Response")
            st.markdown(response_data["text"])
            
            # Play audio if available
            if "audio" in response_data and response_data["audio"]:
                st.session_state['last_audio'] = response_data["audio"]
                st.audio(f"data:audio/mp3;base64,{response_data['audio']}", format="audio/mp3")

        elif response.status_code == 500:
            # Audio generation failed but we have text
            try:
                # Parse the error response
                error_data = response.json()
                
                # Display the text response
                st.subheader("Agent Response")
                st.markdown(error_data["text"])
                
                # Show error message about audio
                st.warning("Audio generation failed. Text response is still available.")
                
                # You can show the specific error if needed
                with st.expander("See error details"):
                    st.error(error_data.get("error", "Unknown error"))
                    
            except Exception as e:
                # If JSON parsing fails for some reason
                st.error(f"Error processing response: {str(e)}")
                st.write(response.text)

        else:
            # Other error cases
            st.error(f"Error: {response.status_code} - {response.text}")

# Button to play last response
if 'last_audio' in st.session_state and st.session_state['last_audio'] and st.button("Play Last Response Again"):
    st.audio(f"data:audio/mp3;base64,{st.session_state['last_audio']}", format="audio/mp3")