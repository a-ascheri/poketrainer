# tests/unit/services/test_jwt.py

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from jose import JWTError
import jwt

from src.services.jwt import (
    create_access_token,
    verify_access_token,
)
from src.config import settings


class TestCreateAccessToken:
    """Tests para create_access_token"""
    
    def test_create_access_token_default_expiration(self):
        """Crear token con expiración por defecto"""
        data = {"sub": "testuser", "role": "trainer"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decodificar y verificar
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "trainer"
        assert "exp" in decoded
    
    def test_create_access_token_custom_expiration(self):
        """Crear token con expiración personalizada"""
        data = {"sub": "admin", "role": "admin"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "admin"
        assert decoded["role"] == "admin"
        
        # Verificar que la expiración es aproximadamente correcta
        exp = decoded["exp"]
        expected_exp = datetime.utcnow() + timedelta(minutes=30)
        # Permitir 5 segundos de diferencia
        assert abs(exp - expected_exp.timestamp()) < 5
    
    def test_create_access_token_with_extra_claims(self):
        """Crear token con claims adicionales"""
        data = {
            "sub": "user123",
            "role": "trainer",
            "force_password_change": True,
            "custom_field": "test"
        }
        token = create_access_token(data)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "trainer"
        assert decoded["force_password_change"] is True
        assert decoded["custom_field"] == "test"
    
    def test_create_access_token_expires_delta_none(self):
        """Crear token sin expires_delta (usa el de settings)"""
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=None)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in decoded


class TestVerifyAccessToken:
    """Tests para verify_access_token"""
    
    def test_verify_valid_token(self):
        """Verificar token válido"""
        token = create_access_token({"sub": "user1", "role": "trainer"})
        payload = verify_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user1"
        assert payload["role"] == "trainer"
    
    def test_verify_expired_token(self):
        """Verificar token expirado - debe retornar None"""
        # Crear token con expiración de 1 minuto
        with patch('src.services.jwt.datetime') as mock_datetime:
            # Fijar tiempo actual para creación
            fake_now = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = fake_now
            
            token = create_access_token({"sub": "user1"}, expires_delta=timedelta(minutes=1))
            
            # Ahora hacer que el tiempo actual sea 10 minutos después
            with patch('src.services.jwt.datetime') as mock_now:
                mock_now.utcnow.return_value = fake_now + timedelta(minutes=10)
                
                payload = verify_access_token(token)
                
                # Debe retornar None porque el token expiró
                assert payload is None
    
    def test_verify_invalid_token(self):
        """Verificar token inválido (mal formado)"""
        payload = verify_access_token("invalid.token.here")
        assert payload is None
    
    def test_verify_malformed_token(self):
        """Verificar token mal formado"""
        payload = verify_access_token("12345")
        assert payload is None
    
    def test_verify_empty_token(self):
        """Verificar token vacío"""
        payload = verify_access_token("")
        assert payload is None
    
    def test_verify_token_wrong_secret(self):
        """Verificar token firmado con otra clave"""
        # Crear token con una clave diferente
        wrong_secret = "wrong_secret_key_123"
        wrong_token = jwt.encode({"sub": "user1"}, wrong_secret, algorithm=settings.ALGORITHM)
        
        payload = verify_access_token(wrong_token)
        
        # Debe retornar None porque la verificación falla
        assert payload is None
    
    def test_verify_token_tampered(self):
        """Verificar token manipulado"""
        token = create_access_token({"sub": "user1"})
        
        # Manipular el token (cambiar un caracter)
        tampered_token = token[:-1] + ('a' if token[-1] != 'a' else 'b')
        
        payload = verify_access_token(tampered_token)
        
        assert payload is None
    
    def test_verify_token_missing_exp(self):
        """Verificar token sin expiración"""
        # Crear token sin expiración manualmente
        no_exp_token = jwt.encode(
            {"sub": "user1"}, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        payload = verify_access_token(no_exp_token)
        
        # Debe decodificarse pero no tiene exp
        assert payload is not None
        assert payload["sub"] == "user1"