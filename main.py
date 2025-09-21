from fastapi import FastAPI

# Create FastAPI instance
app = FastAPI(
    title="Hello World API",
    description="A simple FastAPI backend with a hello world endpoint",
    version="1.0.0"
)

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