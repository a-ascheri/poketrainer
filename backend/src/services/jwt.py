from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import JWTError, jwt

from src.config import settings


# Crear un access token JWT
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crea un token JWT de acceso
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado (opcional)
    
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# Verificar y decodificar un access token JWT
def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica y decodifica un token JWT
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Payload del token si es válido, None en caso contrario
    """
    # Validar que el token no sea None, vacío o solo espacios
    if not token or not isinstance(token, str) or token.strip() == "":
        return None
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # Error general de JWT (token inválido, expirado, firma incorrecta, etc.)
        return None
    except (AttributeError, ValueError):
        # Error por formato inválido del token (None, mal formado, etc.)
        return None
