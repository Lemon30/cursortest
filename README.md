# FastAPI Backend with OpenAI Integration

A FastAPI backend with hello world and OpenAI GPT-4o Mini chat completion endpoints.

## Features

- Hello World endpoint at `/`
- Health check endpoint at `/health`
- OpenAI chat completion endpoint at `/chat/completions`
- LinkedIn job description extraction endpoint at `/extract/job-description`
- Interactive API documentation (Swagger UI)
- Automatic OpenAPI schema generation
- Proper error handling and request validation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure OpenAI API key:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_actual_openai_api_key_here
```

## Running the Application

### Option 1: Using Python directly
```bash
python main.py
```

### Option 2: Using uvicorn command
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Main endpoint**: http://localhost:8000/
- **Health check**: http://localhost:8000/health
- **Chat completion**: http://localhost:8000/chat/completions
- **Job description extraction**: http://localhost:8000/extract/job-description
- **Interactive docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## API Endpoints

### GET /
Returns a hello world message.

**Response:**
```json
{
  "message": "Hello, World!"
}
```

### GET /health
Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### POST /chat/completions
Makes a chat completion request to OpenAI GPT-4o Mini.

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "model": "gpt-4o-mini",
  "max_tokens": 150,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "message": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "model": "gpt-4o-mini",
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 17,
    "total_tokens": 29
  }
}
```

### POST /extract/job-description
Extracts a job description from a LinkedIn job post URL using OpenAI GPT-4o Mini.

Note: LinkedIn may block unauthenticated requests. If the HTML cannot be fetched, the endpoint returns a 400 error.

**Request Body:**
```json
{
  "url": "https://www.linkedin.com/jobs/view/123456789/",
  "model": "gpt-4o-mini",
  "max_tokens": 500,
  "temperature": 0.2
}
```

**Response:**
```json
{
  "job_description": "As a Senior Backend Engineer, you will...",
  "source_url": "https://www.linkedin.com/jobs/view/123456789/",
  "model": "gpt-4o-mini",
  "usage": {
    "prompt_tokens": 800,
    "completion_tokens": 300,
    "total_tokens": 1100
  },
  "raw_text_excerpt": "We are looking for..."
}
```

**Parameters:**
- `url` (required): Full LinkedIn job post URL
- `model` (optional): OpenAI model (default: `gpt-4o-mini`)
- `max_tokens` (optional): Max tokens for the completion (default: 500)
- `temperature` (optional): Creativity (default: 0.2)

**Parameters:**
- `messages` (required): Array of chat messages with role ("user", "assistant", "system") and content
- `model` (optional): OpenAI model to use (default: "gpt-4o-mini")
- `max_tokens` (optional): Maximum tokens in response (default: 150)
- `temperature` (optional): Creativity/randomness (0.0-2.0, default: 0.7)

## Development

For development with auto-reload, use:
```bash
uvicorn main:app --reload
```