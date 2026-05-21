from pydantic import BaseModel, EmailStr
from datetime import datetime


class TrainerBase(BaseModel):
    username: str
    email: EmailStr


class TrainerCreate(TrainerBase):
    password: str


class TrainerRead(TrainerBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
