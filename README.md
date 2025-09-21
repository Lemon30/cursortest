# Simple FastAPI Hello World Backend

A simple FastAPI backend with a hello world endpoint.

## Features

- Hello World endpoint at `/`
- Health check endpoint at `/health`
- Interactive API documentation (Swagger UI)
- Automatic OpenAPI schema generation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
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

## Development

For development with auto-reload, use:
```bash
uvicorn main:app --reload
```