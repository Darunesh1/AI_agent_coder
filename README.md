## Setup

### Prerequisites
- Docker and Docker Compose installed
- GitHub account with Personal Access Token
- LLM API key (Gemini, OpenAI, or local Ollama)

### Installation

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/ai-coder-agent.git
   cd ai-coder-agent
   ```

2. **Configure environment variables**
   ```
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and add your credentials
   nano .env
   ```

3. **Required Environment Variables**
   - `APP_SECRET`: Your unique secret key (match with Google Form submission)
   - `GITHUB_TOKEN`: GitHub Personal Access Token with `repo` and `workflow` scopes
   - `GOOGLE_API_KEY`: Gemini API key from https://aistudio.google.com/app/apikey
   - `LLM_PROVIDER`: Set to `gemini` (or `ollama`, `openai`, `aipipe`)

4. **Start the application**
   ```
   docker compose up
   ```

5. **Test the endpoint**
   ```
   curl http://localhost:8000/health
   ```

### Configuration Options

#### LLM Providers

**Option 1: Google Gemini (Recommended)**
```
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Option 2: Local Ollama**
```
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:1.5b
```

**Option 3: OpenAI**
```
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

**Option 4: AIPipe**
```
LLM_PROVIDER=aipipe
AIPIPE_TOKEN=your_token_here
AIPIPE_GEMINI_MODEL=gemini-2.5-flash-lite
```


