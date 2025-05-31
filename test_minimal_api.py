import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Minimal API for Railway debugging",
        "status": "working"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "minimal-fastapi"}

if __name__ == "__main__":
    uvicorn.run("test_minimal_api:app", host="0.0.0.0", port=8000, reload=True)
