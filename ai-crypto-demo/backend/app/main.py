"""
AI Crypto Demo - FastAPI Backend

A demo application showcasing AI-generated cryptocurrency with real-time simulation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .routers import crypto_router, simulation_router, ai_router, websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 AI Crypto Demo Backend starting...")
    yield
    # Shutdown
    print("👋 AI Crypto Demo Backend shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AI Crypto Demo",
    description="A technical demo showing AI generating and managing a simulated cryptocurrency",
    version="1.0.0",
    lifespan=lifespan,
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(crypto_router)
app.include_router(simulation_router)
app.include_router(ai_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Crypto Demo API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/config")
async def get_config():
    """Get public configuration."""
    return {
        "default_simulation_duration": settings.default_simulation_duration,
        "max_transactions_per_second": settings.max_transactions_per_second,
        "ai_available": bool(settings.anthropic_api_key or settings.openai_api_key),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
