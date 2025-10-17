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

### Security Notes

⚠️ **NEVER commit `.env` file to GitHub!**

- Use `.env.example` as a template
- Keep `.env` in `.gitignore`
- Rotate secrets if accidentally exposed
- Use different secrets for development and production
```

***

## **Commands to Push to GitHub**

```bash
# 1. Ensure .env is gitignored
echo ".env" >> .gitignore

# 2. Create .env.example (already done above)
# Copy the template above to .env.example

# 3. Add files to git
git add .env.example
git add .gitignore
git add README.md

# 4. Commit
git commit -m "Add environment configuration template and setup instructions"

# 5. Push to GitHub
git push origin main
```

***

## **What Gets Pushed vs What Stays Local**

| File | Push to GitHub? | Purpose |
|------|----------------|---------|
| `.env.example` | ✅ YES | Template for others |
| `.env` | ❌ NO | Your actual secrets |
| `.gitignore` | ✅ YES | Protects secrets |
| `README.md` | ✅ YES | Setup instructions |
| Code files | ✅ YES | Application code |
| `docker-compose.yml` | ✅ YES | Docker config |

***

Your `.env.example` file is now ready to push to GitHub, and others can use it as a template by copying it to `.env` and filling in their own credentials! This is the standard practice for open-source projects that require API keys and secrets.
