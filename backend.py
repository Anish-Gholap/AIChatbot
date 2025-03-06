import uvicorn
import os
import base64
import requests
import json

from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, Response, status
from ai_agent import get_response_from_ai_agent
from jigsawstack import JigsawStack
from dotenv import load_dotenv

# Load key
load_dotenv()

app = FastAPI()

# List of approved models
ALLOWED_MODELS = [
  "llama-3.3-70b-versatile", 
  "gpt-4o", 
  "deepseek-r1-distill-qwen-32b", 
  "gemma2-9b-it"
]

# Request Schema
class RequestState(BaseModel):
  model_name: str
  model_provider: str
  system_prompt: str
  messages: List[str]
  allow_search: bool
  tts_enabled: Optional[bool] = False
  voice: Optional[str] = "en-SG-female-1"
  
  
def get_TTS_file(text, voice):
  try:
    # Get TTS from api
    jigsawstack = JigsawStack(api_key=os.getenv("JIGSAWSTACK_API_KEY"))
    response = jigsawstack.audio.text_to_speech({
      "text": text,
      "accent": voice
    })
    
  except Exception as e:
    print(f"Error generating Speech from API: {str(e)}")
    return None
  
  audio_binary = response.content
  
  # Encode binary audio as base64
  audio_base64 = base64.b64encode(audio_binary).decode('utf-8')
  
  return audio_base64
  
  
  
# Routes
@app.post("/chat")
def get_LLM_response(request: RequestState):
  # Check if selected model is allowed
  if request.model_name not in ALLOWED_MODELS:
    return {"error": "invalid model chosen. Choose a valid LLM"}
  
  # Get response from AI Agent
  text_response = get_response_from_ai_agent(
    llm_id=request.model_name,
    provider=request.model_provider,
    allow_search=request.allow_search,
    system_prompt=request.system_prompt,
    query=request.messages
  )
  
  if request.tts_enabled == False:
    return {"text": text_response}
  
  # Get TTS audio file
  audio = get_TTS_file(text=text_response, voice=request.voice)
  
  if audio is None:
    print("Error generating TTS file")
    return Response(
      content=json.dumps({
        "text": text_response,
        "audio": None,
        "error": "Failed to generate audio"
      }),
      media_type= "application/json",
      status_code= status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
  return {
    "text": text_response,
    "audio": audio
  }
    
@app.post("/verify")
def verify_message_from_bot(request: List[str]):
  # Set up AI Agent
  name = "llama-3.3-70b-versatile"
  provider = "Groq"
  system_prompt = "Acting as fact checker, you will verify if the query is real or fake. Use and provide reputable sources and answer in singlish"
  allow_search = True
  voice = "en-SG-female-1"
  
  # Get response from AI Agent
  response = get_response_from_ai_agent(
    llm_id=name,
    provider=provider,
    system_prompt=system_prompt,
    query=request,
    allow_search=allow_search
  )
  
  # Get TTS audio file
  audio = get_TTS_file(text=response, voice=voice)
  
  if audio is None:
    print("Error generating TTS file")
    return Response(
      content=json.dumps({
        "text": response,
        "audio": None,
        "error": "Failed to generate audio"
      }),
      media_type= "application/json",
      status_code= status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
  # Send file to whatsapp server
  request_to_server = {
    "text": response,
    "audio": audio
  }
  
  headers = {
    'Content-Type': 'application/json'
  }
  
  server_url = "http://localhost:3001/reply"
  
  server_response = requests.post(
    server_url, 
    json=request_to_server,
    headers=headers
  )
  
  return server_response.status_code

# Run App
if __name__ == "__main__":
  uvicorn.run(app, host="localhost", port=3000)

  
  