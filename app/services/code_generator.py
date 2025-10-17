from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.schemas.models import ProjectRequest
from app.services.llm_service import get_llm


async def generate_code(request: ProjectRequest) -> dict:
    """
    Generate code based on project brief using configured LLM.
    Returns dict with filenames and content.
    """

    # Get the configured LLM
    llm = get_llm()

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert web developer. Generate clean, minimal code 
        that exactly meets the requirements. Return valid HTML, CSS, and JavaScript.""",
            ),
            (
                "user",
                """Brief: {brief}
        
Requirements:
{checks}

Generate a complete single-page application with:
1. index.html (main file)
2. Any necessary CSS/JS inline or as separate files
3. Professional README.md
4. MIT LICENSE file

Return the code for each file.""",
            ),
        ]
    )

    # Create chain
    chain = prompt | llm | StrOutputParser()

    # Generate code
    response = await chain.ainvoke(
        {
            "brief": request.brief,
            "checks": "\n".join(f"- {check}" for check in request.checks),
        }
    )

    # Parse response into files (you'll need to implement proper parsing)
    return {
        "index.html": response,  # Simplified - implement proper file splitting
        "README.md": "# Project\n\nGenerated project",
        "LICENSE": "MIT License...",
    }
