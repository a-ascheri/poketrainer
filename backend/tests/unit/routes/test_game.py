import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi.testclient import TestClient
from fastapi import HTTPException
import sys
from pathlib import Path
from datetime import datetime

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.main import app
from src.routes.auth_dependencies import require_trainer
from src.models.user import User
from src.schemas.game_save import GameSaveRead

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_auth():
    """Mock de autenticación para todos los tests"""
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.username = "test_trainer"
    mock_user.role = "trainer"
    mock_user.is_active = True
    
    app.dependency_overrides[require_trainer] = lambda: mock_user
    yield mock_user
    app.dependency_overrides.clear()


class TestLoadSave:
    """Tests para GET /api/v1/game/save"""
    
    @patch('src.routes.game.game_service.get_game_save_or_404')
    def test_load_save_success(self, mock_get_save):
        """Cargar partida existente exitosamente"""
        # Crear un objeto con los campos requeridos por GameSaveRead
        mock_save = MagicMock()
        mock_save.id = 1
        mock_save.trainer_id = 1
        mock_save.map_id = "pallet_town"
        mock_save.direction = "down"
        mock_save.inventory = {}
        mock_save.game_flags = {}
        mock_save.created_at = datetime.now()
        mock_save.updated_at = datetime.now()
        mock_get_save.return_value = mock_save
        
        response = client.get("/api/v1/game/save")
        
        assert response.status_code == 200
        mock_get_save.assert_called_once_with(1, ANY)
    
    @patch('src.routes.game.game_service.get_game_save_or_404')
    def test_load_save_not_found(self, mock_get_save):
        """Partida no existe - 404"""
        mock_get_save.side_effect = HTTPException(status_code=404, detail="No existe partida guardada")
        
        response = client.get("/api/v1/game/save")
        
        assert response.status_code == 404


class TestNewGame:
    """Tests para POST /api/v1/game/save (crear nueva partida)"""
    
    @patch('src.routes.game.game_service.create_game_save')
    def test_new_game_success(self, mock_create_save):
        """Crear nueva partida exitosamente"""
        mock_save = MagicMock()
        mock_save.id = 1
        mock_save.trainer_id = 1
        mock_save.map_id = "pallet_town"
        mock_save.direction = "down"
        mock_save.inventory = {}
        mock_save.game_flags = {}
        mock_save.created_at = datetime.now()
        mock_save.updated_at = datetime.now()
        mock_create_save.return_value = mock_save
        
        response = client.post("/api/v1/game/save")
        
        assert response.status_code == 201
        mock_create_save.assert_called_once_with(1, ANY)
    
    @patch('src.routes.game.game_service.create_game_save')
    def test_new_game_already_exists(self, mock_create_save):
        """Partida ya existe - 409"""
        mock_create_save.side_effect = HTTPException(status_code=409, detail="Ya existe una partida")
        
        response = client.post("/api/v1/game/save")
        
        assert response.status_code == 409
    
    @patch('src.routes.game.game_service.create_game_save')
    def test_new_game_no_starter(self, mock_create_save):
        """Trainer sin starter seleccionado - 400"""
        mock_create_save.side_effect = HTTPException(status_code=400, detail="El entrenador debe seleccionar su starter")
        
        response = client.post("/api/v1/game/save")
        
        assert response.status_code == 400


class TestSaveGame:
    """Tests para PUT /api/v1/game/save (actualizar partida)"""
    
    @patch('src.routes.game.game_service.update_game_save')
    def test_save_game_success(self, mock_update_save):
        """Actualizar partida exitosamente"""
        mock_save = MagicMock()
        mock_save.id = 1
        mock_save.trainer_id = 1
        mock_save.map_id = "route_1"
        mock_save.direction = "up"
        mock_save.inventory = {"potion": 5}
        mock_save.game_flags = {"starter_chosen": True}
        mock_save.created_at = datetime.now()
        mock_save.updated_at = datetime.now()
        mock_update_save.return_value = mock_save
        
        response = client.put(
            "/api/v1/game/save",
            json={"badges": ["boulder", "cascade"]}
        )
        
        assert response.status_code == 200
        mock_update_save.assert_called_once_with(1, ANY, ANY)
    
    @patch('src.routes.game.game_service.update_game_save')
    def test_save_game_not_found(self, mock_update_save):
        """Partida no existe - 404"""
        mock_update_save.side_effect = HTTPException(status_code=404, detail="Partida no encontrada")
        
        response = client.put(
            "/api/v1/game/save",
            json={"badges": ["boulder"]}
        )
        
        assert response.status_code == 404


class TestSetPartySlot:
    """Tests para POST /api/v1/game/save/party/{slot_position}"""
    
    @patch('src.routes.game.game_service.set_party_slot')
    @patch('src.routes.game.game_service.get_game_save_or_404')
    def test_set_party_slot_success(self, mock_get_save, mock_set_slot):
        """Asignar pokémon a slot exitosamente"""
        mock_set_slot.return_value = MagicMock()
        
        mock_save = MagicMock()
        mock_save.id = 1
        mock_save.trainer_id = 1
        mock_save.map_id = "pallet_town"
        mock_save.direction = "down"
        mock_save.inventory = {}
        mock_save.game_flags = {}
        mock_save.created_at = datetime.now()
        mock_save.updated_at = datetime.now()
        mock_get_save.return_value = mock_save
        
        response = client.post(
            "/api/v1/game/save/party/2",
            params={"trainer_pokemon_id": 5}
        )
        
        assert response.status_code == 200
        mock_set_slot.assert_called_once_with(1, 5, 2, ANY)
    
    @patch('src.routes.game.game_service.set_party_slot')
    def test_set_party_slot_invalid_position(self, mock_set_slot):
        """Posición inválida - 400"""
        mock_set_slot.side_effect = HTTPException(status_code=400, detail="slot_position debe estar entre 0 y 5")
        
        response = client.post(
            "/api/v1/game/save/party/6",
            params={"trainer_pokemon_id": 5}
        )
        
        assert response.status_code == 400
    
    @patch('src.routes.game.game_service.set_party_slot')
    def test_set_party_slot_pokemon_not_found(self, mock_set_slot):
        """Pokémon no pertenece al trainer - 404"""
        mock_set_slot.side_effect = HTTPException(status_code=404, detail="Pokémon no encontrado")
        
        response = client.post(
            "/api/v1/game/save/party/0",
            params={"trainer_pokemon_id": 999}
        )
        
        assert response.status_code == 404


class TestRemovePartySlot:
    """Tests para DELETE /api/v1/game/save/party/{slot_position}"""
    
    @patch('src.routes.game.game_service.remove_party_slot')
    @patch('src.routes.game.game_service.get_game_save_or_404')
    def test_remove_party_slot_success(self, mock_get_save, mock_remove_slot):
        """Remover pokémon del slot exitosamente"""
        mock_remove_slot.return_value = None
        
        mock_save = MagicMock()
        mock_save.id = 1
        mock_save.trainer_id = 1
        mock_save.map_id = "pallet_town"
        mock_save.direction = "down"
        mock_save.inventory = {}
        mock_save.game_flags = {}
        mock_save.created_at = datetime.now()
        mock_save.updated_at = datetime.now()
        mock_get_save.return_value = mock_save
        
        response = client.delete("/api/v1/game/save/party/1")
        
        assert response.status_code == 200
        mock_remove_slot.assert_called_once_with(1, 1, ANY)
    
    @patch('src.routes.game.game_service.remove_party_slot')
    def test_remove_party_slot_not_found(self, mock_remove_slot):
        """Slot vacío - 404"""
        mock_remove_slot.side_effect = HTTPException(status_code=404, detail="No hay pokémon en ese slot")
        
        response = client.delete("/api/v1/game/save/party/5")
        
        assert response.status_code == 404
    
    @patch('src.routes.game.game_service.remove_party_slot')
    def test_remove_party_slot_last_pokemon(self, mock_remove_slot):
        """No permite remover el último pokémon - 400"""
        mock_remove_slot.side_effect = HTTPException(status_code=400, detail="El entrenador debe tener al menos 1 pokémon")
        
        response = client.delete("/api/v1/game/save/party/0")
        
        assert response.status_code == 400