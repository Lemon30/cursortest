import os
import re
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from openai import OpenAI
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time

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

def scrape_linkedin_job(url: str) -> dict:
    """
    Scrape LinkedIn job post data
    Returns job title, company, location, and description
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
        
        # Extract job title
        job_title = ""
        title_selectors = [
            'h1.top-card-layout__title',
            'h1[data-automation-id="jobPostingHeader"]',
            'h1.jobs-unified-top-card__job-title',
            'h1'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                job_title = title_element.get_text(strip=True)
                break
        
        # Extract company name
        company = ""
        company_selectors = [
            'a.topcard__org-name-link',
            'a[data-automation-id="jobPostingCompanyLink"]',
            '.jobs-unified-top-card__company-name a',
            '.topcard__flavor--black-link'
        ]
        
        for selector in company_selectors:
            company_element = soup.select_one(selector)
            if company_element:
                company = company_element.get_text(strip=True)
                break
        
        # Extract location
        location = ""
        location_selectors = [
            '.topcard__flavor--bullet',
            '[data-automation-id="jobPostingLocation"]',
            '.jobs-unified-top-card__bullet'
        ]
        
        for selector in location_selectors:
            location_element = soup.select_one(selector)
            if location_element:
                location = location_element.get_text(strip=True)
                break
        
        # Extract job description
        description = ""
        description_selectors = [
            '.description__text',
            '[data-automation-id="jobPostingDescription"]',
            '.jobs-description-content__text',
            '.jobs-box__html-content'
        ]
        
        for selector in description_selectors:
            desc_element = soup.select_one(selector)
            if desc_element:
                description = desc_element.get_text(separator='\n', strip=True)
                break
        
        # Clean up description text
        if description:
            # Remove extra whitespace and normalize line breaks
            description = re.sub(r'\n+', '\n', description)
            description = re.sub(r' +', ' ', description)
        
        return {
            "job_title": job_title or "Not found",
            "company": company or "Not found", 
            "location": location or "Not found",
            "description": description or "Job description not found"
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch LinkedIn page: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing LinkedIn page: {str(e)}")

async def process_job_description_with_gpt(job_data: dict, extract_format: str) -> str:
    """
    Process job description using GPT to extract and structure information
    """
    if extract_format == "raw":
        return job_data["description"]
    
    # Create a structured prompt for GPT
    prompt = f"""
    Please analyze and structure this LinkedIn job posting information:

    Job Title: {job_data["job_title"]}
    Company: {job_data["company"]}
    Location: {job_data["location"]}
    
    Raw Job Description:
    {job_data["description"]}
    
    Please provide a clean, well-structured summary that includes:
    1. Key responsibilities
    2. Required qualifications
    3. Preferred qualifications (if mentioned)
    4. Benefits/perks (if mentioned)
    5. Company information (if mentioned)
    
    Format the response in a clear, professional manner with proper headings and bullet points.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional job description analyzer. Extract and structure job posting information clearly and professionally."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
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
        
        # Scrape LinkedIn job data
        job_data = scrape_linkedin_job(url_str)
        
        # Process with GPT
        processed_description = await process_job_description_with_gpt(job_data, request.extract_format)
        
        processing_time = time.time() - start_time
        
        return LinkedInJobResponse(
            job_title=job_data["job_title"],
            company=job_data["company"],
            location=job_data["location"],
            job_description=processed_description,
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