from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import Optional
from app.state import models


def commit_session(db: Session):
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise


# ------------------- Session CRUD -------------------
def create_session(db: Session, user_id: str) -> models.Session:
    new_session = models.Session(user_id=user_id)
    db.add(new_session)
    commit_session(db)
    db.refresh(new_session)
    return new_session


def get_session(db: Session, session_id: int) -> Optional[models.Session]:
    """
    Fetch a session by its ID.
    Returns Session instance or None if not found.
    """
    return db.query(models.Session).filter(models.Session.id == session_id).first()


# ------------------- Document CRUD -------------------
def create_document(
    db: Session, 
    session_id: int | None,  # allow None
    filename: str, 
    blob_url: Optional[str] = None
) -> models.Document:
    doc = models.Document(
        session_id=session_id, 
        name=filename, 
        blob_url=blob_url
    )
    db.add(doc)
    commit_session(db)
    db.refresh(doc)
    return doc



def get_document_by_id(db: Session, doc_id: int) -> Optional[models.Document]:
    return db.query(models.Document).filter(models.Document.id == doc_id).first()


# ------------------- Chunk CRUD -------------------
def add_chunk(
    db: Session, 
    document_id: int, 
    text: str, 
    embedding: Optional[str] = None
) -> models.Chunk:
    chunk = models.Chunk(
        document_id=document_id, 
        text=text, 
        embedding=embedding
    )
    db.add(chunk)
    commit_session(db)
    db.refresh(chunk)
    return chunk
