import os 
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage

# Load API keys
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setup required LLMs and Tools
gpt_model = ChatOpenAI(model='gpt-4o')
groq_model = ChatGroq(model='llama-3.3-70b-versatile')
search_tool = TavilySearchResults(max_results=2)

# Define a function to generate response from the AI Agent
def get_response_from_ai_agent(llm_id, provider, allow_search, query, system_prompt):
  
  # Select LLM provider based on choice
  if provider == "Groq":
    llm = ChatGroq(model=llm_id)
  elif provider == "OpenAI":
    llm = ChatOpenAI(model=llm_id)
  
  # Define tools available for AI Agent to use
  tools = [TavilySearchResults(max_results=2)] if allow_search else []
  
  # Create the agent
  agent = create_react_agent(
    model=llm,
    tools=tools,
    state_modifier=system_prompt
  )
  
  # Generate and return response
  state={"messages": query}
  response = agent.invoke(state)
  messages = response.get("messages")
  ai_messages = [message.content for message in messages if isinstance(message, AIMessage)]
  
  return ai_messages[-1]
