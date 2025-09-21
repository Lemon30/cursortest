import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="Hello World API with OpenAI",
    description="A FastAPI backend with hello world and OpenAI GPT-4o Mini chat completion endpoints",
    version="1.0.0"
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4o-mini"
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7

class ChatCompletionResponse(BaseModel):
    message: str
    model: str
    usage: dict

class JobDescriptionRequest(BaseModel):
    url: str
    model: Optional[str] = "gpt-4o-mini"
    max_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.2

class JobDescriptionResponse(BaseModel):
    job_description: str
    source_url: str
    model: str
    usage: dict
    raw_text_excerpt: Optional[str] = None

def _extract_job_text_from_html(html: str) -> str:
    """
    Attempt to extract the main job description text from LinkedIn (or similar) HTML.
    Uses several known selectors and falls back to full page text if needed.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    selectors = [
        "div.description__text",
        "div.show-more-less-html__markup",
        "section.description",
        "div.jobs-description-content__text",
        "div.jobs-box__html-content",
        "section[data-test-description-section]",
        "article",
    ]

    text_candidates: List[str] = []
    for selector in selectors:
        for element in soup.select(selector):
            text = element.get_text(separator=" ", strip=True)
            text = " ".join(text.split())
            if len(text) > 200:  # ignore very short fragments
                text_candidates.append(text)

    if text_candidates:
        best_text = max(text_candidates, key=len)
    else:
        # Fallback: full page text
        best_text = soup.get_text(separator=" ", strip=True)
        best_text = " ".join(best_text.split())

    # Truncate to avoid sending extremely long contexts
    if len(best_text) > 18000:
        best_text = best_text[:18000]

    return best_text

@app.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """
    Chat completion endpoint using OpenAI GPT-4o Mini
    Makes a single chat completion API request to OpenAI
    """
    try:
        # Validate API key is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        # Convert Pydantic models to dict format expected by OpenAI
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Make the OpenAI API call
        response = client.chat.completions.create(
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Extract the response content
        message_content = response.choices[0].message.content
        
        return ChatCompletionResponse(
            message=message_content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
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

@app.post("/extract/job-description", response_model=JobDescriptionResponse)
async def extract_job_description(request: JobDescriptionRequest):
    """
    Extract job description from a LinkedIn job post URL using OpenAI GPT-4o Mini.

    1) Fetch the page HTML
    2) Extract visible job text from the HTML
    3) Ask the model to return a clean job description
    """
    try:
        # Validate API key is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
            )

        # Validate URL
        parsed = urlparse(request.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL provided")

        # Fetch the page
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        resp = requests.get(request.url, headers=headers, timeout=20)
        if resp.status_code != 200 or not resp.text:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch URL (status {resp.status_code}). LinkedIn may block unauthenticated requests.",
            )

        page_text = _extract_job_text_from_html(resp.text)
        if not page_text or len(page_text) < 200:
            # Still try to pass what we have, but warn
            page_text = page_text or ""

        system_prompt = (
            "You are an expert HR assistant. Given raw page text from a job posting, "
            "return ONLY the cleaned job description prose. Remove navigation, legal "
            "footers, cookie notices, and duplicate boilerplate. Do not invent details."
        )

        user_prompt = (
            f"Source URL: {request.url}\n\n"
            "Raw page text:\n" + page_text
        )

        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        job_description = response.choices[0].message.content.strip()

        return JobDescriptionResponse(
            job_description=job_description,
            source_url=request.url,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            raw_text_excerpt=page_text[:500] if page_text else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        if "api_key" in str(e).lower():
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
        elif "quota" in str(e).lower():
            raise HTTPException(status_code=429, detail="OpenAI API quota exceeded")
        else:
            raise HTTPException(status_code=500, detail=f"Error extracting job description: {str(e)}")

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