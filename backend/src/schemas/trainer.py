from datetime import datetime

from pydantic import BaseModel, EmailStr


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


# Para updates parciales
class TrainerUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
