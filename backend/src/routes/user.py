from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from ..database.database import get_db
from ..schemas.user import UserCreate, UserRead
from src.services.user_service import create_user as create_user_service, authenticate_user
from src.services.jwt import create_access_token, verify_access_token
from authlib.oauth2.rfc7636 import create_s256_code_challenge
import secrets
import time


# Almacenamiento temporal de códigos de autorización (en memoria, solo para demo)
# en desarrollo usar una base de datos o caché como Redis
authorization_codes = {}
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def create_user(user: UserCreate, db: Session = Depends(get_db)):
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
        "expires_at": time.time() + 600  # 10 minutos
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
    code_verifier: str = Form(...)
):
    data = authorization_codes.get(code)
    
    if not data or data["expires_at"] < time.time():
        raise HTTPException(status_code=400, detail="Código inválido o expirado")
    
    if data["client_id"] != client_id or data["redirect_uri"] != redirect_uri:
        raise HTTPException(status_code=400, detail="Datos de cliente o redirect_uri inválidos")
    
    if data["code_challenge_method"] == "S256":
        expected_challenge = create_s256_code_challenge(code_verifier)
    else:
        expected_challenge = code_verifier  
    
    if expected_challenge != data["code_challenge"]:
        raise HTTPException(status_code=400, detail="PKCE inválido")
    
    access_token = create_access_token({"sub": data["username"]})
    del authorization_codes[code]
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload
