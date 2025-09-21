import os
import re
import json
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from openai import OpenAI
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="LinkedIn Job Extractor API with OpenAI",
    description="A FastAPI backend with LinkedIn job post extraction, GPT processing, and chat completion endpoints",
    version="1.0.0"
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def scrape_linkedin_job(url: str) -> str:
    """
    Scrape LinkedIn job post HTML content
    Returns the full HTML text for GPT processing
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # Add delay to be respectful to LinkedIn's servers
        time.sleep(1)
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements to clean up the HTML
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Get the text content with some structure preserved
        html_text = soup.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace while preserving structure
        html_text = re.sub(r'\n\s*\n', '\n\n', html_text)  # Normalize multiple newlines
        html_text = re.sub(r' +', ' ', html_text)  # Normalize spaces
        
        # Limit the text size to avoid token limits (keep first 15000 characters)
        if len(html_text) > 15000:
            html_text = html_text[:15000] + "... [truncated]"
        
        return html_text
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch LinkedIn page: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing LinkedIn page: {str(e)}")

async def process_job_description_with_gpt(html_content: str, extract_format: str) -> dict:
    """
    Process LinkedIn job HTML content using GPT to extract and structure information
    """
    if extract_format == "raw":
        return {
            "job_title": "Raw HTML Content",
            "company": "N/A",
            "location": "N/A",
            "description": html_content
        }
    
    # Create a comprehensive prompt for GPT to extract all job information
    prompt = f"""
    You are analyzing a LinkedIn job posting page. Extract the following information from this HTML content:

    HTML Content:
    {html_content}
    
    Please extract and return the following information in JSON format:
    {{
        "job_title": "exact job title",
        "company": "company name",
        "location": "job location",
        "description": "structured job description with clear sections"
    }}
    
    For the description, please structure it professionally with clear sections including:
    - Key responsibilities
    - Required qualifications
    - Preferred qualifications (if mentioned)
    - Benefits/perks (if mentioned)
    - Company information (if mentioned)
    
    Format the description with proper headings and bullet points for readability.
    If any information is not found, use "Not found" as the value.
    
    Return ONLY the JSON object, no additional text.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional job information extractor. Extract job details from LinkedIn HTML content and return them in the exact JSON format requested. Be thorough and accurate."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        # Parse the JSON response from GPT
        gpt_response = response.choices[0].message.content.strip()
        
        # Remove any markdown formatting if present
        if gpt_response.startswith("```json"):
            gpt_response = gpt_response[7:]
        if gpt_response.endswith("```"):
            gpt_response = gpt_response[:-3]
        
        try:
            job_data = json.loads(gpt_response)
            return job_data
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "job_title": "Parsing Error",
                "company": "Parsing Error",
                "location": "Parsing Error",
                "description": gpt_response
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT processing error: {str(e)}")

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

class LinkedInJobRequest(BaseModel):
    url: HttpUrl
    extract_format: Optional[str] = "structured"  # "structured" or "raw"

class LinkedInJobResponse(BaseModel):
    job_title: str
    company: str
    location: str
    job_description: str
    extracted_url: str
    processing_time: float

@app.post("/linkedin/job", response_model=LinkedInJobResponse)
async def extract_linkedin_job(request: LinkedInJobRequest):
    """
    Extract and process LinkedIn job posting using GPT
    Accepts a LinkedIn job post URL and returns structured job information
    """
    start_time = time.time()
    
    try:
        # Validate API key is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        # Validate LinkedIn URL
        url_str = str(request.url)
        if "linkedin.com" not in url_str or "/jobs/" not in url_str:
            raise HTTPException(
                status_code=400, 
                detail="Invalid LinkedIn job URL. Please provide a valid LinkedIn job posting URL."
            )
        
        # Scrape LinkedIn job HTML content
        html_content = scrape_linkedin_job(url_str)
        
        # Process with GPT to extract job information
        job_data = await process_job_description_with_gpt(html_content, request.extract_format)
        
        processing_time = time.time() - start_time
        
        return LinkedInJobResponse(
            job_title=job_data["job_title"],
            company=job_data["company"],
            location=job_data["location"],
            job_description=job_data["description"],
            extracted_url=url_str,
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

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