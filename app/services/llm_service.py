import httpx
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.config import LLMProvider, settings


class AIPipeGemini(BaseChatModel):
    """Custom LangChain wrapper for Gemini via AIPipe.org"""

    token: str
    model: str = "gemini-2.5-flash-lite"
    temperature: float = 0.7
    max_tokens: int = 4096

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Sync generation - not implemented for this async-focused wrapper"""
        raise NotImplementedError("Use ainvoke() for async calls")

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        """Async generation using AIPipe's Gemini API"""
        # Convert LangChain messages to Gemini format
        contents = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                contents.append({"parts": [{"text": msg.content}], "role": "user"})
            elif isinstance(msg, SystemMessage):
                # Gemini doesn't have system role, prepend as user message
                contents.insert(
                    0,
                    {
                        "parts": [{"text": f"Instructions: {msg.content}"}],
                        "role": "user",
                    },
                )
            elif isinstance(msg, AIMessage):
                contents.append(
                    {"parts": [{"text": msg.content}], "role": "model"}
                )  # FIXED: removed extra quote

        # Call AIPipe Gemini endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://aipipe.org/geminiv1beta/models/{self.model}:generateContent",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={
                    "contents": contents,
                    "generationConfig": {
                        "temperature": self.temperature,
                        "maxOutputTokens": self.max_tokens,
                    },
                },
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()

        # Extract response text
        try:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise ValueError(
                f"Unexpected AIPipe Gemini response format: {result}"
            ) from e

        # Return in LangChain format
        message = AIMessage(content=text)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "aipipe-gemini"


def get_llm() -> BaseChatModel:
    """
    Returns the configured LLM based on environment settings.
    Supports OpenAI, Google Gemini, AIPipe, and Ollama.
    """
    if settings.llm_provider == LLMProvider.OPENAI:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.llm_temperature,
            api_key=settings.openai_api_key,
        )

    elif settings.llm_provider == LLMProvider.GEMINI:
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required when using Gemini provider")

        # Fix: Add 'models/' prefix if not present
        gemini_model = settings.gemini_model
        if not gemini_model.startswith("models/"):
            gemini_model = f"models/{gemini_model}"

        return ChatGoogleGenerativeAI(
            model=gemini_model,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_tokens,
            google_api_key=settings.google_api_key,
        )

    elif settings.llm_provider == LLMProvider.AIPIPE:
        if not settings.aipipe_token:
            raise ValueError("AIPIPE_TOKEN is required when using AIPipe provider")
        return AIPipeGemini(
            token=settings.aipipe_token,
            model=settings.aipipe_gemini_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    elif settings.llm_provider == LLMProvider.OLLAMA:
        return ChatOllama(
            model=settings.ollama_model,
            temperature=settings.llm_temperature,
            num_predict=settings.llm_max_tokens,
            base_url=settings.ollama_base_url,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def get_llm_with_fallback() -> BaseChatModel:
    """
    Returns LLM with automatic fallback support.
    Falls back from OpenAI -> Gemini -> AIPipe -> Ollama if primary fails.
    """
    llms = []

    # Try to create all available LLMs
    if settings.openai_api_key:
        llms.append(
            ChatOpenAI(
                model=settings.openai_model,
                temperature=settings.llm_temperature,
                max_retries=0,
            )
        )

    if settings.google_api_key:
        gemini_model = settings.gemini_model
        if not gemini_model.startswith("models/"):
            gemini_model = f"models/{gemini_model}"

        llms.append(
            ChatGoogleGenerativeAI(
                model=gemini_model,
                temperature=settings.llm_temperature,
                max_retries=0,
            )
        )

    if settings.aipipe_token:
        llms.append(
            AIPipeGemini(
                token=settings.aipipe_token,
                model=settings.aipipe_gemini_model,
                temperature=settings.llm_temperature,
            )
        )

    # Ollama as last resort
    llms.append(
        ChatOllama(
            model=settings.ollama_model,
            temperature=settings.llm_temperature,
            base_url=settings.ollama_base_url,
        )
    )

    if not llms:
        raise ValueError("No LLM providers configured")

    # Set up fallback chain
    primary_llm = llms[0]
    if len(llms) > 1:
        return primary_llm.with_fallbacks(llms[1:])
    return primary_llm
