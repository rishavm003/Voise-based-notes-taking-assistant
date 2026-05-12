import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, notes
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Pre-load ML models
    logger.info("Loading ML models...")
    from app.services import transcriber
    from app.ml import classifier, extractor
    try:
        transcriber.load_whisper_model()
        classifier.load_classifier()
        extractor.load_spacy_model()
        logger.info("All models loaded. API ready.")
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        # In production you might want to fail fast here
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(notes.router)

from app.models.note import Note
from app.schemas.note import NotePublicResponse
from sqlalchemy import select
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException

@app.get("/share/{share_token}", response_model=NotePublicResponse)
async def get_public_note(
    share_token: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Note).filter(Note.share_token == share_token))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note

@app.get("/")
async def root():
    return {"message": "Welcome to the Smart Voice Notes API", "version": "1.0.0"}
