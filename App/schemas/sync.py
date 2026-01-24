# App/schemas/vector_sync_state.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class VectorSyncStateBase(BaseModel):
    """Base schema for VectorSyncState (used for input)"""
    entity_name: str
    last_synced_at: Optional[datetime] = None

class VectorSyncStateCreate(VectorSyncStateBase):
    """Schema for creating a new sync record"""
    pass

class VectorSyncStateUpdate(BaseModel):
    """Schema for updating the sync state"""
    last_synced_at: datetime

class VectorSyncStateRead(VectorSyncStateBase):
    """Schema for reading sync state (output)"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # <-- important for SQLAlchemy integration
