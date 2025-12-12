"""
FastAPI Backend for TechScopeAI
Provides REST API endpoints for all agents
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import routes
from backend.api.routes import auth, pitch, marketing, patent, policy, team, competitive, chat

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("TechScopeAI API Starting...")
    print(f"   OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Missing'}")
    print(f"   Gemini API Key: {'Set' if os.getenv('GEMINI_API_KEY') else 'Missing'}")
    print(f"   Weaviate: {'Enabled' if os.getenv('USE_WEAVIATE_QUERY_AGENT', '').lower() == 'true' else 'Disabled'}")
    yield
    # Shutdown
    print("TechScopeAI API Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="TechScopeAI API",
    description="AI-powered startup toolkit API - Pitch decks, marketing, patents, policies, and more",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
# Get allowed origins from environment (for production) or use defaults (for development)
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")
if ALLOWED_ORIGINS_ENV:
    # Production: use environment variable (comma-separated)
    allowed_origins = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",")]
else:
    # Development: use localhost origins
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3003",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(pitch.router, prefix="/api/pitch", tags=["Pitch Agent"])
app.include_router(marketing.router, prefix="/api/marketing", tags=["Marketing Agent"])
app.include_router(patent.router, prefix="/api/patent", tags=["Patent Agent"])
app.include_router(policy.router, prefix="/api/policy", tags=["Policy Agent"])
app.include_router(team.router, prefix="/api/team", tags=["Team Agent"])
app.include_router(competitive.router, prefix="/api/competitive", tags=["Competitive Agent"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "TechScopeAI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "weaviate": os.getenv("USE_WEAVIATE_QUERY_AGENT", "").lower() == "true"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

