import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="Hello World API with OpenAI",
    description="A FastAPI backend with hello world and OpenAI GPT-5 Nano chat completion endpoints",
    version="1.0.0"
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models
class ChatCompletionRequest(BaseModel):
    input: str
    model: Optional[str] = "gpt-5-nano"
    max_output_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7
    reasoning_effort: Optional[str] = "medium"  # minimal, low, medium, high
    verbosity: Optional[str] = "medium"  # low, medium, high
    top_p: Optional[float] = None
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    message: str
    model: str
    usage: dict
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None

@app.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """
    Chat completion endpoint using OpenAI GPT-5 Nano
    Makes a single chat completion API request to OpenAI
    """
    try:
        # Validate API key is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        # Prepare parameters for GPT-5 Nano API call
        api_params = {
            "model": request.model,
            "input": request.input,
            "max_output_tokens": request.max_output_tokens,
            "temperature": request.temperature,
            "reasoning_effort": request.reasoning_effort,
            "verbosity": request.verbosity,
            "stream": request.stream
        }
        
        # Add optional parameters only if they're not None
        if request.top_p is not None:
            api_params["top_p"] = request.top_p
        
        # Make the OpenAI API call for GPT-5
        response = client.chat.completions.create(**api_params)
        
        # Extract the response content
        message_content = response.choices[0].message.content
        
        return ChatCompletionResponse(
            message=message_content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            reasoning_effort=request.reasoning_effort,
            verbosity=request.verbosity
        )
        
    except Exception as e:
        if "api_key" in str(e).lower():
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
        elif "quota" in str(e).lower():
            raise HTTPException(status_code=429, detail="OpenAI API quota exceeded")
        elif "model" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"Invalid model specified: {request.model}")
        else:
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

@app.get("/")
async def hello_world():
    """
    Hello World endpoint
    Returns a simple greeting message
    """
    return {"message": "Hello, World!"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns the status of the API
    """
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)