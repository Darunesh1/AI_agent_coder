from typing import List

from app.schemas.models import Attachment
from app.services.llm_service import get_llm


class CodeGenerator:
    def __init__(self):
        self.llm = get_llm()

    async def generate_application(
        self, brief: str, checks: List[str], attachments: List[Attachment]
    ) -> str:
        """
        Generate complete HTML application based on brief and checks.
        Returns:
            str: Complete HTML code as string.
        """
        # Format checks
        checks_text = "\n".join(f"  {i + 1}. {check}" for i, check in enumerate(checks))

        # Format attachments info
        attachments_text = ""
        if attachments:
            attachments_text = "\n\nATTACHMENTS PROVIDED:\n"
            for att in attachments:
                attachments_text += f"  - {att.name} (data URI provided)\n"

        prompt = f"""You are an expert web developer. Create a complete, production-ready single-page HTML application.

TASK BRIEF:
{brief}

EVALUATION CHECKS (your app MUST pass all these):
{checks_text}
{attachments_text}

REQUIREMENTS:
1. Create a SINGLE self-contained HTML file with inline CSS and JavaScript
2. Use Bootstrap 5 from CDN: https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
3. Make it responsive and professional-looking
4. Include proper error handling and loading states
5. Ensure ALL checks will pass when tested
6. Use semantic HTML and clean code structure
7. Add comments to explain key functionality

CRITICAL: Return ONLY the raw HTML code. No explanations, no markdown formatting, no code blocks. Just the HTML starting with <!DOCTYPE html>.
"""

        response = await self.llm.ainvoke(prompt)
        code = response.content.strip()

        # Clean up markdown formatting if LLM added it
        if code.startswith("```html"):
            code = code[7:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]

        return code.strip()

    async def generate_readme(self, task_id: str, brief: str) -> str:
        """
        Generate professional README.md content.
        Returns:
            str: README content as string.
        """
        prompt = f"""Create a professional README.md for this web application project.

Project ID: {task_id}
Brief: {brief}

Include these sections:
1. # [Meaningful Project Title]
2. ## Overview (2-3 sentences about what this does)
3. ## Features (bullet points of key functionality)
4. ## Usage (how to use the application)
5. ## Technical Details (brief code explanation)
6. ## License (MIT)

Make it concise, professional, and well-formatted in Markdown.
Return ONLY the README content, no extra text.
"""

        response = await self.llm.ainvoke(prompt)
        return response.content.strip()
