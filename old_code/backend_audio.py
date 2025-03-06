import uvicorn
from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, Response
from ai_agent import get_response_from_ai_agent
from jigsawstack import JigsawStack
import os
from dotenv import load_dotenv
import base64
import requests


# Load environment variables
load_dotenv()


# Get API key
JIGSAWSTACK_API_KEY = os.getenv("JIGSAWSTACK_API_KEY")

# Define the request schema for pydantic to validate
class RequestState(BaseModel):
    model_name: str  # defines model name eg gpt-40
    model_provider: str  # defines model provider eg OpenAI
    system_prompt: str  # defines system behaviour in generating prompt
    messages: List[str]  # 
    allow_search: bool  # allows agent to search web
    tts_enabled: Optional[bool] = False  # whether to generate speech
    voice_name: Optional[str] = "en-SG-female-1"  # voice to use for TTS

# Setup endpoints to handle frontend requests for the AI Agent
app = FastAPI()

# List of approved models
ALLOWED_MODELS = ["llama-3.3-70b-versatile", "gpt-4o", "deepseek-r1-distill-qwen-32b", "gemma2-9b-it"]

# Function to generate speech from text
def generate_tts(text, voice_name):
    try:
        # Initialize the JigsawStack client
        jigsaw = JigsawStack(api_key=JIGSAWSTACK_API_KEY)
        
        # Use the client to generate speech
        response = jigsaw.audio.text_to_speech({
            "text": text,
            "accent": voice_name
        })
        
        # Return the audio content
        return response.content
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return None

@app.post("/chat")
def chat_endpoint(request: RequestState):
    """
    API endpoint to interact with the Chatbot using LangGraph and search tools.
    Dynamically selects model specified in the request
    """
    
    # Check if model specified is approved for use
    if request.model_name not in ALLOWED_MODELS:
        return {"error": "invalid model chosen. Choose a valid LLM"}
    
    # Create AI agent to generate response for request
    text_response = get_response_from_ai_agent(
        llm_id=request.model_name,
        provider=request.model_provider,
        allow_search=request.allow_search,
        system_prompt=request.system_prompt,
        query=request.messages    
    )
    
    # If TTS is not enabled, just return the text response
    if not request.tts_enabled:
        return text_response
    
    # Generate TTS if enabled
    audio_content = generate_tts(text_response, request.voice_name)
    
    # If audio generation failed, return just the text
    if audio_content is None:
        return {"text": text_response, "audio": None, "error": "Failed to generate audio"}
    
    # Encode the audio to base64 for transmission
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
    
    # Return both text and audio
    return {
        "text": text_response,
        "audio": audio_base64
    }

# Add an endpoint to only generate TTS from text
@app.post("/tts")
def tts_endpoint(request: dict):
    """
    API endpoint to generate TTS from text
    """
    text = request.get("text", "")
    voice = request.get("voice", "en-SG-female-1")
    
    if not text:
        return {"error": "No text provided"}
    
    # Generate TTS
    audio_content = generate_tts(text, voice)
    
    # If audio generation failed
    if audio_content is None:
        return {"error": "Failed to generate audio"}
    
    # Return the audio as a binary response
    return Response(
        content=audio_content,
        media_type="audio/mpeg"
    )
    
    
@app.post("/whatsapp")
def send_response_to_bot(request):
  
  # Prepare request for LLM
  llm_request = RequestState(
    model_name="llama-3.3-70b-versatile",
    model_provider="Groq",
    system_prompt="Act as a fact checker who will determine if the query is real or fake. Only use reputable sources and provide them in your reply. Reply back in singlish",
    allow_search=True,
    tts_enabled=True,
    voice_name="en-SG-female-1"
  )
  
  llm_response = get_response_from_ai_agent(
    llm_id=llm_request.model_name,
    provider=llm_request.model_provider,
    query=request,
    system_prompt=llm_request.system_prompt
  )
  
  # Generate TTS if enabled
  audio_content = generate_tts(llm_response, request.voice_name)
  
  # If audio generation failed, return just the text
  if audio_content is None:
      return {"text": llm_response, "audio": None, "error": "Failed to generate audio"}
  
  # Encode the audio to base64 for transmission
  audio_base64 = base64.b64encode(audio_content).decode('utf-8')
  
  # Return both text and audio
  request_bot = {
      "text": llm_response,
      "audio": audio_base64
  }

  bot_url = "http://localhost:3001/reply"

  headers = {
      'Content-Type': 'application/json'
  }

  response = requests.post(bot_url, json=request_bot, headers=headers)
  
  return response.status_code  

# Run App 
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)