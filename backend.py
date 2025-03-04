import uvicorn
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from ai_agent import get_response_from_ai_agent

# Define the request schema for pydantic to validate
class RequestState(BaseModel):
  model_name: str # defines model name eg gpt-40
  model_provider: str # defines model provider eg OpenAI
  system_prompt: str # defines system behaviour in generating prompt
  messages: List[str] # 
  allow_search: bool # allows agent to search web 
  
# Setup endpoints to handle frontend requests for the AI Agent
app = FastAPI()

# List of approved models
ALLOWED_MODELS = ["llama-3.3-70b-versatile", "gpt-4o"]

@app.post("/chat")
def chat_endpoint(request: RequestState):
  """
  API endpoint to interact with the Chatbot using LangGraph and search tools.
  Dynamically selects model specified in the request
  """
  
  # check if model specified is approved for use
  if request.model_name not in ALLOWED_MODELS:
    return {"error": "invalid model chosen. Choose a valid LLM"}
  
  # Create AI agent to generate response for request
  response = get_response_from_ai_agent(
    llm_id=request.model_name,
    provider=request.model_provider,
    allow_search=request.allow_search,
    system_prompt=request.system_prompt,
    query=request.messages    
  )
  
  return response


# Run App 
if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=3000)
  
