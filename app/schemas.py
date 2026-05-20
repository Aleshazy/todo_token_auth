from datetime import datetime
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    expires_at: datetime

class TodoCreate(BaseModel):
    title: str
    description: str | None = None

class TodoStatusUpdate(BaseModel):
    is_complete: bool

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_complete: bool

    class Config:
        from_attributes = True

class PendingCountResponse(BaseModel):
    pending_count: int