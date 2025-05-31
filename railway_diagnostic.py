import os
import socket
import sys
import platform
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "active",
        "message": "Railway diagnostic tool is running"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "railway-diagnostic"
    }

@app.get("/diagnostic")
async def diagnostic():
    # Collect system information
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    # Collect environment variables (excluding sensitive ones)
    env_vars = {k: v for k, v in os.environ.items() 
               if not any(sensitive in k.lower() for sensitive in 
                         ["key", "token", "secret", "password", "auth"])}
    
    # Port information
    port = int(os.getenv("PORT", 8000))
    
    return {
        "status": "active",
        "system": {
            "hostname": hostname,
            "ip": ip_address,
            "platform": platform.platform(),
            "python_version": platform.python_version()
        },
        "railway": {
            "environment": os.getenv("RAILWAY_ENVIRONMENT"),
            "service": os.getenv("RAILWAY_SERVICE"),
            "project": os.getenv("RAILWAY_PROJECT_NAME")
        },
        "network": {
            "port": port,
            "port_env_var": os.getenv("PORT")
        },
        "environment": env_vars
    }

if __name__ == "__main__":
    print("Starting Railway diagnostic tool...")
    # Try port 8080 locally to avoid conflicts
    try:
        port = int(os.getenv("PORT", 8080))
        print(f"Attempting to bind to 0.0.0.0:{port}")
        uvicorn.run("railway_diagnostic:app", host="0.0.0.0", port=port)
    except OSError:
        # If port is in use, try another port
        fallback_port = 8090
        print(f"Port {port} in use, trying {fallback_port}")
        uvicorn.run("railway_diagnostic:app", host="0.0.0.0", port=fallback_port)
