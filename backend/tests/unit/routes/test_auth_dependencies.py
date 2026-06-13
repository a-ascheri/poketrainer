# tests/unit/routes/test_auth_dependencies.py

import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi import HTTPException
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.routes.auth_dependencies import (
    get_current_user,
    get_current_user_entity,
    require_admin,
    require_trainer,
)
from src.services.jwt import create_access_token


class TestGetCurrentUser:
    """Tests para get_current_user"""
    
    @patch('src.routes.auth_dependencies.verify_access_token')
    def test_get_current_user_valid_token(self, mock_verify):
        """Token válido - retorna payload"""
        mock_verify.return_value = {"sub": "1", "role": "trainer"}
        
        result = get_current_user("valid_token")
        
        assert result is not None
        assert result["sub"] == "1"
        assert result["role"] == "trainer"
        mock_verify.assert_called_once_with("valid_token")
    
    @patch('src.routes.auth_dependencies.verify_access_token')
    def test_get_current_user_invalid_token(self, mock_verify):
        """Token inválido - lanza 401"""
        mock_verify.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user("invalid_token")
        
        assert exc_info.value.status_code == 401
        assert "Token invalido o expirado" in str(exc_info.value.detail)


class TestGetCurrentUserEntity:
    """Tests para get_current_user_entity"""
    
    @patch('src.routes.auth_dependencies.get_user_by_id')
    def test_get_current_user_entity_valid(self, mock_get_user):
        """Payload válido - retorna entidad User"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # CORREGIDO: pasar payload directamente, no como kwarg
        payload = {"sub": "1", "role": "trainer"}
        result = get_current_user_entity(payload=payload, db=MagicMock())
        
        assert result is not None
        assert result.id == 1
        mock_get_user.assert_called_once_with(1, ANY)
    
    def test_get_current_user_entity_no_sub(self):
        """Payload sin 'sub' - lanza 401"""
        payload = {"role": "trainer"}  # Sin sub
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_entity(payload=payload, db=MagicMock())
        
        assert exc_info.value.status_code == 401
        assert "Token invalido" in str(exc_info.value.detail)


class TestRequireAdmin:
    """Tests para require_admin"""
    
    def test_require_admin_success(self):
        """Usuario admin válido"""
        mock_user = MagicMock()
        mock_user.role = "admin"
        mock_user.force_password_change = False
        
        result = require_admin(mock_user)
        
        assert result == mock_user
    
    def test_require_admin_force_password_change(self):
        """Admin con password change pendiente - 403"""
        mock_user = MagicMock()
        mock_user.role = "admin"
        mock_user.force_password_change = True
        
        with pytest.raises(HTTPException) as exc_info:
            require_admin(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Password change required" in str(exc_info.value.detail)
    
    def test_require_admin_wrong_role(self):
        """Usuario no admin - 403"""
        mock_user = MagicMock()
        mock_user.role = "trainer"
        mock_user.force_password_change = False
        
        with pytest.raises(HTTPException) as exc_info:
            require_admin(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Admin role required" in str(exc_info.value.detail)


class TestRequireTrainer:
    """Tests para require_trainer"""
    
    def test_require_trainer_success(self):
        """Usuario trainer válido"""
        mock_user = MagicMock()
        mock_user.role = "trainer"
        mock_user.force_password_change = False
        
        result = require_trainer(mock_user)
        
        assert result == mock_user
    
    def test_require_trainer_force_password_change(self):
        """Trainer con password change pendiente - 403"""
        mock_user = MagicMock()
        mock_user.role = "trainer"
        mock_user.force_password_change = True
        
        with pytest.raises(HTTPException) as exc_info:
            require_trainer(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Password change required" in str(exc_info.value.detail)
    
    def test_require_trainer_wrong_role(self):
        """Usuario no trainer - 403"""
        mock_user = MagicMock()
        mock_user.role = "admin"
        mock_user.force_password_change = False
        
        with pytest.raises(HTTPException) as exc_info:
            require_trainer(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Trainer role required" in str(exc_info.value.detail)


class TestIntegrationWithRealToken:
    """Tests de integración con token real"""
    
    @patch('src.routes.auth_dependencies.get_user_by_id')
    @patch('src.routes.auth_dependencies.get_db')
    def test_real_token_flow(self, mock_db, mock_get_user):
        """Flujo real: crear token -> validar -> obtener usuario"""
        # Crear token real
        token = create_access_token({"sub": "1", "role": "trainer"})
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        
        # Obtener payload
        payload = get_current_user(token)
        assert payload["sub"] == "1"
        
        # Obtener entidad
        user = get_current_user_entity(payload=payload, db=mock_db)
        assert user.id == 1