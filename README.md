# LinkedIn Job Extractor API with OpenAI Integration

A FastAPI backend with LinkedIn job post extraction, GPT processing, hello world, and OpenAI GPT-4o Mini chat completion endpoints.

## Features

- LinkedIn job post extraction endpoint at `/linkedin/job`
- GPT-powered job description processing and structuring
- Hello World endpoint at `/`
- Health check endpoint at `/health`
- OpenAI chat completion endpoint at `/chat/completions`
- Interactive API documentation (Swagger UI)
- Automatic OpenAPI schema generation
- Proper error handling and request validation
- Web scraping with respectful rate limiting

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
- **LinkedIn job extractor**: http://localhost:8000/linkedin/job
- **Chat completion**: http://localhost:8000/chat/completions
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

### POST /linkedin/job
Extracts and processes LinkedIn job posting information using GPT.

**Request Body:**
```json
{
  "url": "https://www.linkedin.com/jobs/view/1234567890",
  "extract_format": "structured"
}
```

**Response:**
```json
{
  "job_title": "Senior Software Engineer",
  "company": "Tech Company Inc.",
  "location": "San Francisco, CA",
  "job_description": "## Key Responsibilities\n- Develop and maintain web applications\n- Collaborate with cross-functional teams\n\n## Required Qualifications\n- 5+ years of software development experience\n- Proficiency in Python, JavaScript\n\n## Benefits\n- Competitive salary\n- Health insurance\n- Remote work options",
  "extracted_url": "https://www.linkedin.com/jobs/view/1234567890",
  "processing_time": 3.45
}
```

**Parameters:**
- `url` (required): LinkedIn job post URL
- `extract_format` (optional): "structured" for GPT-processed format or "raw" for original text (default: "structured")

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