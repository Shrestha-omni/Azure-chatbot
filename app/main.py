# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from loguru import logger

from app.config.settings import settings
from app.state.db import Base, engine, get_db
from app.routers import sessions, upload, process, chat

# -------------------------
# App Initialization
# -------------------------
app = FastAPI(
    title="RAG Azure API",
    description="Document ingestion and retrieval API using Azure OpenAI, Blob Storage, and FAISS",
    version="1.0.0"
)

# -------------------------
# Middleware
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Include Routers
# -------------------------
app.include_router(sessions.router, prefix="/session", tags=["sessions"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(process.router, prefix="/process", tags=["process"])
app.include_router(chat.router)


# -------------------------
# Startup / Shutdown Events
# -------------------------
@app.on_event("startup")
def startup_event():
    try:
        # Initialize DB tables
        logger.info("🔧 Creating database tables if not exist...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables ready")
    except Exception as e:
        logger.error(f"❌ Failed to initialize DB: {e}")

@app.on_event("shutdown")
def shutdown_event():
    logger.info("👋 Shutting down RAG Azure API...")

# -------------------------
# Optional root endpoint
# -------------------------
@app.get("/")
def root():
    return {"message": "RAG Azure API is running!"}
