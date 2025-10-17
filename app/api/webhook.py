import asyncio

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.config import settings
from app.schemas.models import EvaluationPayload, TaskRequest, TaskResponse
from app.services.code_generator import CodeGenerator
from app.services.github_service import GitHubService

router = APIRouter()


@router.post("/task", response_model=TaskResponse)
async def receive_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Main webhook endpoint to receive task requests
    """
    # Step 1: Validate secret
    if request.secret != settings.app_secret:
        raise HTTPException(status_code=401, detail="Invalid secret")

    # Step 2: Return immediate 200 OK
    response = TaskResponse(
        status="accepted",
        message=f"Task {request.task} round {request.round} accepted for processing",
        task=request.task,
    )

    # Step 3: Process in background
    background_tasks.add_task(process_task, request)

    return response


async def process_task(request: TaskRequest):
    """
    Background task processor
    """
    try:
        print(f"🚀 Processing task: {request.task} (Round {request.round})")

        # Initialize services
        github_service = GitHubService(settings.github_token)
        code_generator = CodeGenerator()

        # Step 1: Generate application code
        print("📝 Generating application code...")
        index_html = await code_generator.generate_application(
            brief=request.brief, checks=request.checks, attachments=request.attachments
        )

        # Step 2: Generate README
        print("📄 Generating README...")
        readme_md = await code_generator.generate_readme(
            task_id=request.task, brief=request.brief
        )

        # Step 3: Execute Git workflow
        print("🔧 Executing Git workflow...")
        git_result = github_service.git_workflow(
            task_id=request.task,
            brief=request.brief,
            index_html=index_html,
            readme_md=readme_md,
        )

        # Step 4: Submit to evaluation URL
        print("📤 Submitting to evaluation URL...")
        await submit_to_evaluation(
            evaluation_url=request.evaluation_url,
            email=request.email,
            task=request.task,
            round=request.round,
            nonce=request.nonce,
            repo_url=git_result["repo_url"],
            commit_sha=git_result["commit_sha"],
            pages_url=git_result["pages_url"],
        )

        print(f"✅ Task {request.task} completed successfully!")

    except Exception as e:
        print(f"❌ Error processing task {request.task}: {e}")
        import traceback

        traceback.print_exc()


async def submit_to_evaluation(
    evaluation_url: str,
    email: str,
    task: str,
    round: int,
    nonce: str,
    repo_url: str,
    commit_sha: str,
    pages_url: str,
    max_retries: int = 5,
):
    """
    Submit results to evaluation URL with exponential backoff retry
    """
    payload = EvaluationPayload(
        email=email,
        task=task,
        round=round,
        nonce=nonce,
        repo_url=repo_url,
        commit_sha=commit_sha,
        pages_url=pages_url,
    )

    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    evaluation_url,
                    json=payload.model_dump(),
                    headers={"Content-Type": "application/json"},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    print(f"✅ Successfully submitted to evaluation URL")
                    return
                else:
                    print(
                        f"⚠️ Evaluation URL returned {response.status_code}: {response.text}"
                    )

            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed: {e}")

            # Exponential backoff: 1s, 2s, 4s, 8s, 16s
            if attempt < max_retries - 1:
                await asyncio.sleep(2**attempt)

    raise Exception("Failed to submit to evaluation URL after all retries")
