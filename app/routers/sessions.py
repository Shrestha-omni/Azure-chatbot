# app/routers/sessions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.state import repos
from app.state.db import get_db

router = APIRouter()

# -------------------------------
# Pydantic Models
# -------------------------------
class SessionCreateRequest(BaseModel):
    user_id: str

class SessionResponse(BaseModel):
    sessionId: str
    userId: str
    createdAt: str  # ISO format


# -------------------------------
# Routes
# -------------------------------
@router.post("/", response_model=dict)
def start_session(data: SessionCreateRequest, db: Session = Depends(get_db)):
    """
    Start a new session for a given user_id.
    Returns session_id.
    """
    session = repos.create_session(db=db, user_id=data.user_id)
    return {"sessionId": session.session_id}


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieve session info by session_id.
    Raises 404 if session not found.
    """
    session = repos.create_session(db=db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "sessionId": session.session_id,
        "userId": session.user_id,
        "createdAt": session.created_at.isoformat()
    }
