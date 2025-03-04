import streamlit as st
import requests

# Setup the frontend using streamlit
st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("AI ChatBot Agent")
st.write("Create and Interact with AI Agents")

# Get User input

# Text box for system prompt
system_prompt = st.text_area("Define your AI Agent: ", height=70, placeholder="Type your system prompt here...")

# Radio buttons to select model provider
MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile"]
MODEL_NAMES_OPENAI = ['gpt-4o']

provider = st.radio("Select Provider:", ("Groq", "OpenAI"))

if provider == "Groq":
  selected_model = st.selectbox("Select Groq Model:", MODEL_NAMES_GROQ)
else:
  selected_model = st.selectbox("Select OpenAI Model:", MODEL_NAMES_OPENAI)

# Checkbox for web search
allow_web_search = st.checkbox("Allow Web Search")

# Text box for user query
user_query =  st.text_area("Enter your query: ", height=150, placeholder="Ask Anything!")

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
        st.markdown(f"Final Reponse: {response_data}")
  
  

