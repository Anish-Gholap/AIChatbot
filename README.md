# AI Chatbot with Text-to-Speech

A versatile AI chatbot application that uses large language models with a built-in text-to-speech feature. This application allows users to interact with various AI models through a simple interface and receive both text and audio responses.

## Features

- **Multiple AI Models**: Support for various LLMs from Groq and OpenAI
- **Text-to-Speech**: Convert AI responses to natural-sounding speech using JigsawStack
- **Web Search Capability**: Enable the AI to search the web for up-to-date information using Tavily
- **Customizable System Prompts**: Define how the AI should behave with custom instructions
- **Voice Selection**: Choose from different voice options for the text-to-speech feature
- **Error Handling**: Graceful handling of errors during text-to-speech generation

## Architecture

The application follows a client-server architecture:

- **Frontend**: Streamlit-based user interface
- **Backend**: FastAPI server that handles AI model interactions and text-to-speech generation
- **AI Agent**: Uses LangGraph's ReAct agent for reasoning and tool use

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- API keys for:
  - Groq (for Llama models)
  - OpenAI (for GPT models)
  - Tavily (for web search)
  - JigsawStack (for text-to-speech)

### Environment Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with the following:
   ```
   GROQ_API_KEY=your_groq_api_key
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   JIGSAWSTACK_API_KEY=your_jigsawstack_api_key
   ```

## Running the Application

1. Start the backend server:
   ```
   python backend.py
   ```
   This will start the FastAPI server on http://localhost:3000

2. Start the frontend application:
   ```
   streamlit run frontend.py
   ```
   This will open the Streamlit interface in your web browser

## API Endpoints

### `/chat`

Process user queries and generate AI responses with optional text-to-speech.

**Request Body:**
```json
{
  "model_name": "llama-3.3-70b-versatile",
  "model_provider": "Groq",
  "system_prompt": "You are a helpful assistant",
  "messages": ["What is machine learning?"],
  "allow_search": true,
  "tts_enabled": true,
  "voice": "en-SG-female-1"
}
```

**Response (Success):**
```json
{
  "text": "Machine learning is a branch of artificial intelligence...",
  "audio": "base64_encoded_audio_data"
}
```

**Response (TTS Failure):**
```json
{
  "text": "Machine learning is a branch of artificial intelligence...",
  "audio": null,
  "error": "Failed to generate audio"
}
```

### `/verify`

Verify information and respond with a fact-check in Singlish. This endpoint is designed to work with a WhatsApp bot.

**Request Body:**
```json
["Is it true that Singapore has the world's best airport?"]
```

**Response:**
Returns the status code from the WhatsApp server.

## Project Structure

- `frontend.py`: Streamlit user interface
- `backend.py`: FastAPI server with endpoints for AI interaction
- `ai_agent.py`: Implementation of the LangGraph ReAct agent

## Supported Models

### Groq Models
- llama-3.3-70b-versatile
- deepseek-r1-distill-qwen-32b
- gemma2-9b-it

### OpenAI Models
- gpt-4o

## Voice Options

- en-SG-female-1
- en-SG-male-1

## Error Handling

The application includes robust error handling for:
- Invalid model selection
- Text-to-speech generation failures
- API connectivity issues

## Future Improvements

- Add conversation history support
- Implement more voice options
- Add support for additional LLM providers
- Create a mobile app interface

## License

[Add your license information here]

## Contributors

[Add contributor information here]
