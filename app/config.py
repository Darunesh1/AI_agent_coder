from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    AIPIPE = "aipipe"


class Settings(BaseSettings):
    # Your secret from Google Form
    app_secret: str

    # GitHub
    github_token: str

    # LLM Provider Selection
    llm_provider: LLMProvider = LLMProvider.GEMINI  # Changed default to GEMINI

    # OpenAI Configuration
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # Google Gemini Configuration (Direct API)
    google_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash-lite"  # FIXED: Updated to valid model

    # AIPipe Configuration (for proxied Gemini access)
    aipipe_token: str | None = None
    aipipe_gemini_model: str = "gemini-2.5-flash-lite"  # FIXED: Updated to valid model

    # Ollama Configuration (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Common LLM settings
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096

    # DuckDB path (optional for logging)
    duckdb_path: str = "data/ai_coder.duckdb"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
