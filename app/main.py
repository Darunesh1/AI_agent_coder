from fastapi import FastAPI

from app.api import webhook

app = FastAPI(
    title="AI Coder Agent",
    description="LLM-powered code deployment agent",
    version="1.0.0",
)

# Include API routers
# app.include_router(webhook.router, prefix="/api", tags=["webhook"])


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "AI Coder Agent is running! 🚀",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "ai_coder"}


@app.get("/test")
async def test():
    """Test endpoint"""
    return {
        "message": "FastAPI is working!",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }
