import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services.auth import get_current_user
from app.services import redis_service, transcriber, s3_storage
from app.ml import classifier, extractor
import os
import tempfile
import logging
import secrets
from app.schemas.note import NotePublicResponse

# Existing routes...

@router.post("/{note_id}/share")
async def share_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Note).filter(Note.id == note_id, Note.user_id == current_user.id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if not note.share_token:
        note.share_token = secrets.token_urlsafe(12)
        await db.commit()
        await db.refresh(note)
    
    return {"share_url": f"/share/{note.share_token}", "token": note.share_token}

@router.delete("/{note_id}/share")
async def revoke_share(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Note).filter(Note.id == note_id, Note.user_id == current_user.id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.share_token = None
    await db.commit()
    
    return {"message": "Link revoked"}

logger = logging.getLogger(__name__)

@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Check cache first
    cached_notes = await redis_service.get_notes_cache(str(current_user.id))
    if cached_notes:
        return cached_notes

    # DB query on miss
    result = await db.execute(select(Note).filter(Note.user_id == current_user.id).order_by(Note.created_at.desc()))
    notes = result.scalars().all()
    
    # Set cache
    notes_data = [NoteResponse.model_validate(n).model_dump() for n in notes]
    await redis_service.set_notes_cache(str(current_user.id), notes_data)
    
    return notes

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_note = Note(
        **note_in.model_dump(),
        user_id=current_user.id
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    
    # Invalidate cache
    await redis_service.invalidate_notes_cache(str(current_user.id))
    
    return new_note

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Note).filter(Note.id == note_id, Note.user_id == current_user.id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    note_in: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Note).filter(Note.id == note_id, Note.user_id == current_user.id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    update_data = note_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    await db.commit()
    await db.refresh(note)
    
    # Invalidate cache
    await redis_service.invalidate_notes_cache(str(current_user.id))
    
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Note).filter(Note.id == note_id, Note.user_id == current_user.id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Also delete audio from Cloudinary if exists
    if note.cloudinary_public_id:
        await cloudinary.delete_audio(note.cloudinary_public_id)
        
    await db.delete(note)
    await db.commit()
    
    # Invalidate cache
    await redis_service.invalidate_notes_cache(str(current_user.id))
    
    return None

def generate_intelligent_title(content: str, keywords: List[str], category: str) -> str:
    """
    Generates a smart title based on keywords and category.
    """
    if not keywords:
        return content[:50].strip() + "..." if len(content) > 50 else content
    
    # Use top 2 keywords
    main_keywords = ", ".join([k.capitalize() for k in keywords[:2]])
    return f"{category.capitalize()}: {main_keywords}"

@router.post("/transcribe", status_code=status.HTTP_201_CREATED)
async def transcribe_voice_note(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    transcript_json: Optional[Dict[str, str]] = Body(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 0. RATE LIMITING
    is_allowed = await redis_service.check_rate_limit(str(current_user.id), "transcribe")
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Max {settings.RATE_LIMIT_TRANSCRIBE} transcriptions per minute."
        )

    transcript_text = None
    audio_url = None
    cloudinary_id = None
    temp_orig = None
    temp_wav = None
    
    # Case A: Audio File Provided (Server-side Transcription)
    if file:
        # 1. VALIDATION
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(status_code=415, detail="Unsupported audio format")

        contents = await file.read()
        if len(contents) > settings.MAX_AUDIO_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File too large. Max {settings.MAX_AUDIO_SIZE_MB}MB.")
        
        try:
            # 2. SAVE TO TEMP
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                tmp.write(contents)
                temp_orig = tmp.name
            
            # 3. S3 / R2 UPLOAD
            logger.info(f"Uploading audio for user {current_user.id} to Cloudflare R2...")
            object_name = f"audio/{current_user.id}/{uuid.uuid4()}.mp3"
            audio_url = await s3_storage.storage.upload_file(temp_orig, object_name)
            cloudinary_id = object_name # Store S3 key for later deletion

            # 4. PREPROCESS & TRANSCRIBE
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_w:
                temp_wav = tmp_w.name
            
            transcriber.preprocess_audio(temp_orig, temp_wav)
            transcript = transcriber.transcribe_audio(temp_wav)
            transcript_text = transcript["text"]

        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            if cloudinary_id:
                await cloudinary.delete_audio(cloudinary_id)
            raise HTTPException(status_code=500, detail="Transcription pipeline failed")
    
    # Case B: Text Provided (Client-side Transcription)
    elif transcript_json and "transcript" in transcript_json:
        transcript_text = transcript_json["transcript"]
    
    else:
        raise HTTPException(status_code=400, detail="No audio file or transcript text provided")

    if not transcript_text or not transcript_text.strip():
        if cloudinary_id:
            await s3_storage.storage.delete_file(cloudinary_id)
        raise HTTPException(status_code=422, detail="Empty transcript. Please speak clearly.")

    # 6. CLASSIFY & EXTRACT
    try:
        category, confidence = classifier.predict_category(transcript_text)
        keywords = extractor.extract_keywords(transcript_text)
        
        # 8. SAVE TO DB
        title = generate_intelligent_title(transcript_text, keywords, category)
        
        new_note = Note(
            user_id=current_user.id,
            title=title,
            content=transcript_text,
            category=category,
            keywords=keywords,
            audio_url=audio_url,
            cloudinary_public_id=cloudinary_id
        )
        
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)

        # Invalidate notes cache
        await redis_service.invalidate_notes_cache(str(current_user.id))

        # Cleanup
        def cleanup_files(paths):
            for p in paths:
                if p and os.path.exists(p):
                    try: os.remove(p)
                    except: pass
        background_tasks.add_task(cleanup_files, [temp_orig, temp_wav])

        return {
            "note": new_note,
            "ml_metadata": {
                "category": category,
                "confidence": confidence,
                "keywords": keywords
            }
        }

    except Exception as e:
        logger.error(f"Enrichment error: {e}")
        raise HTTPException(status_code=500, detail="Failed to enrich note with ML metadata")

