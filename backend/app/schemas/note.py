import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class NoteBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: str
    category: Optional[str] = "uncategorized"
    is_public: bool = False

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None

class NoteResponse(NoteBase):
    id: uuid.UUID
    user_id: uuid.UUID
    keywords: List[str] = []
    audio_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NotePublicResponse(BaseModel):
    title: Optional[str]
    content: str
    category: Optional[str]
    keywords: List[str] = []
    audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
