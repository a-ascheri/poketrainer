from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class AdminCreate(UserBase):
    password: str
    permissions: list[str] = ["manage_users", "manage_admins"]


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None


class ChangePasswordInput(BaseModel):
    current_password: str
    new_password: str


class UserRead(UserBase):
    id: int
    role: str
    permissions: list[str] = []
    force_password_change: bool
    starter_pokemon_selected: bool
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    force_password_change: bool
