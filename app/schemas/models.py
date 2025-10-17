from typing import List, Optional

from pydantic import BaseModel, EmailStr


class Attachment(BaseModel):
    """Attachment model for files sent with task"""

    name: str
    url: str  # data URI format


class TaskRequest(BaseModel):
    """Request model for incoming task webhook"""

    email: EmailStr
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: List[Attachment] = []


class TaskResponse(BaseModel):
    """Response model for task webhook"""

    status: str
    message: str
    task: str


class EvaluationPayload(BaseModel):
    """Payload to send to evaluation URL"""

    email: EmailStr
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str
