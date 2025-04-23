from pydantic import BaseModel


class ProcessingResult(BaseModel):
    session_phone: str
    spam_blocked: bool
    renewed_session: bool
