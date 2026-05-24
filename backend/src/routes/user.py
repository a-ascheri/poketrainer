import secrets
import time

from authlib.oauth2.rfc7636 import create_s256_code_challenge
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.services.jwt import create_access_token, verify_access_token
from src.services.user_service import (
    ADMIN_ROLE,
    TRAINER_ROLE,
    authenticate_user,
    change_password,
    create_admin_user,
    create_user as create_user_service,
    get_user_by_id,
)

from ..database.database import get_db
from ..schemas.user import (
    AdminCreate,
    ChangePasswordInput,
    LoginResponse,
    UserCreate,
    UserRead,
)

# Almacenamiento temporal de códigos de autorización (en memoria, solo para demo)
# en desarrollo usar una base de datos o caché como Redis
authorization_codes = {}
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")



# Endpoint para crear usuario
@router.post(
    "/users/",
    response_model=UserRead,
    summary="Registro público de trainer",
    description="Crea un usuario con rol trainer para acceso al juego.",
)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(user, db)


# Authorization Code con PKCE
# Guardar info temporalmente (en prod usar DB o cache)
# Redirigir con el código
@router.get("/authorize")
async def authorize(
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    code_challenge_method: str = "S256",
    username: str = None,
    password: str = None,
    db: Session = Depends(get_db),
):
    user = authenticate_user(username, password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    code = secrets.token_urlsafe(32)
    authorization_codes[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "username": username,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "expires_at": time.time() + 600,  # 10 minutos
    }
    url = f"{redirect_uri}?code={code}&state=xyz"
    return {"code": code, "redirect_uri": redirect_uri, "state": "xyz"}


# Buscar el código
# Validar PKCE
# Solo para demo, en prod usar S256
# Generar access_token (JWT)
# Eliminar el código (one-time use)
@router.post("/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    code_verifier: str = Form(...),
):
    data = authorization_codes.get(code)

    if not data or data["expires_at"] < time.time():
        raise HTTPException(status_code=400, detail="Código inválido o expirado")

    if data["client_id"] != client_id or data["redirect_uri"] != redirect_uri:
        raise HTTPException(
            status_code=400, detail="Datos de cliente o redirect_uri inválidos"
        )

    if data["code_challenge_method"] == "S256":
        expected_challenge = create_s256_code_challenge(code_verifier)
    else:
        expected_challenge = code_verifier

    if expected_challenge != data["code_challenge"]:
        raise HTTPException(status_code=400, detail="PKCE inválido")

    access_token = create_access_token({"sub": data["username"]})
    del authorization_codes[code]
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/login",
    summary="Login con JWT",
    description="Autentica usuario y retorna token con rol y estado de cambio de contraseña.",
)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> LoginResponse:
    user = authenticate_user(username, password, db)
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role,
            "force_password_change": user.force_password_change,
        }
    )
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        force_password_change=user.force_password_change,
    )


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload


def get_current_user_entity(
    payload: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    return get_user_by_id(int(user_id), db)


def require_admin(current_user=Depends(get_current_user_entity)):
    if current_user.force_password_change:
        raise HTTPException(
            status_code=403,
            detail="Password change required before using admin endpoints",
        )
    if current_user.role != ADMIN_ROLE:
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user


def require_trainer(current_user=Depends(get_current_user_entity)):
    if current_user.force_password_change:
        raise HTTPException(
            status_code=403,
            detail="Password change required before using trainer endpoints",
        )
    if current_user.role != TRAINER_ROLE:
        raise HTTPException(status_code=403, detail="Trainer role required")
    return current_user


@router.post(
    "/users/me/change-password",
    summary="Cambio de contraseña",
    description="Permite completar el cambio forzado de contraseña en primer login.",
)
def change_password_route(
    payload: ChangePasswordInput,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_entity),
):
    return change_password(current_user, payload, db)


@router.get(
    "/users/me",
    response_model=UserRead,
    summary="Perfil autenticado",
    description="Devuelve perfil del usuario autenticado para control de rol y onboarding.",
)
def current_user_profile(current_user=Depends(get_current_user_entity)):
    return current_user


@router.post("/internal/admins", response_model=UserRead, include_in_schema=False)
def create_admin_route(
    payload: AdminCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return create_admin_user(payload, db)
