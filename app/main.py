from fastapi import FastAPI

from app.api import webhook
from app.config import LLMProvider, settings
from app.services.llm_service import get_llm

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


@app.get("/test-llm")
async def test_llm():
    """Test the configured LLM"""
    try:
        llm = get_llm()
        response = await llm.ainvoke(
            "Say 'Hello from AI Coder Agent!' in one sentence."
        )

        return {
            "provider": settings.llm_provider.value,
            "model": get_current_model_name(),
            "response": response.content,
            "status": "success",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_current_model_name() -> str:
    """Helper to get current model name"""
    if settings.llm_provider == LLMProvider.OPENAI:
        return settings.openai_model
    elif settings.llm_provider == LLMProvider.GEMINI:
        return settings.gemini_model
    elif settings.llm_provider == LLMProvider.AIPIPE:
        return settings.aipipe_gemini_model
    elif settings.llm_provider == LLMProvider.OLLAMA:
        return settings.ollama_model
    else:
        return "unknown"
