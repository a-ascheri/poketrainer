import secrets
import time

from authlib.oauth2.rfc7636 import create_s256_code_challenge
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from src.routes.auth_dependencies import get_current_user_entity
from src.routes.prefixes import USER_PREFIX
from src.services.jwt import create_access_token
from src.services.user_service import authenticate_user, change_password
from src.services.user_service import create_user as create_user_service

from ..database.database import get_db
from ..schemas.user import ChangePasswordInput, LoginResponse, UserCreate, UserRead

# Almacenamiento temporal de códigos de autorización (en memoria, solo para demo)
# en desarrollo usar una base de datos o caché como Redis
authorization_codes = {}
router = APIRouter(prefix=USER_PREFIX, tags=["User"])


@router.post("/register", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crea un usuario con rol trainer para acceso al juego.

    Args:
        user (UserCreate): Datos del usuario a crear.
        db (Session): Sesión de base de datos.

    Returns:
        UserRead: Usuario creado.
    """
    return create_user_service(user, db)


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
    """
    Autoriza a un usuario y genera un código de autorización temporal (PKCE).

    Args:
        client_id (str): ID del cliente OAuth.
        redirect_uri (str): URI de redirección.
        code_challenge (str): Challenge PKCE.
        code_challenge_method (str): Método PKCE (por defecto S256).
        username (str): Nombre de usuario.
        password (str): Contraseña.
        db (Session): Sesión de base de datos.

    Returns:
        dict: Código de autorización y URI de redirección.
    """
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
    return {"code": code, "redirect_uri": redirect_uri, "state": "xyz"}


# Buscar el código, Validar PKCE, Solo para demo, en prod usar S256
# Generar access_token (JWT), Eliminar el código (one-time use)
@router.post("/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    code_verifier: str = Form(...),
):
    """
    Intercambia un código de autorización por un access token JWT (PKCE).

    Args:
        grant_type (str): Tipo de grant OAuth.
        code (str): Código de autorización.
        redirect_uri (str): URI de redirección.
        client_id (str): ID del cliente OAuth.
        code_verifier (str): Verificador PKCE.

    Returns:
        dict: Access token y tipo.
    """
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
)
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Autentica usuario y retorna token JWT con rol y estado de cambio de contraseña.

    Args:
        username (str): Nombre de usuario.
        password (str): Contraseña.
        db (Session): Sesión de base de datos.

    Returns:
        LoginResponse: Token JWT y datos de autenticación.
    """
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


@router.post(
    "/change-password",
)
def change_password_for_current_user(
    payload: ChangePasswordInput,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_entity),
):
    """
    Permite completar el cambio forzado de contraseña en primer login.

    Args:
        payload (ChangePasswordInput): Datos para el cambio de contraseña.
        db (Session): Sesión de base de datos.
        current_user: Usuario autenticado.

    Returns:
        UserRead: Usuario con contraseña actualizada.
    """
    return change_password(current_user, payload, db)


@router.get(
    "/profile",
    response_model=UserRead,
)
def get_profile(current_user=Depends(get_current_user_entity)):
    """
    Devuelve el perfil del usuario autenticado para control de rol y onboarding.

    Args:
        current_user: Usuario autenticado.

    Returns:
        UserRead: Perfil del usuario autenticado.
    """
    return current_user

