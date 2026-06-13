# tests/unit/services/test_game_service.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.services.game_service import (
    get_game_save,
    get_game_save_or_404,
    create_game_save,
    update_game_save,
    set_party_slot,
    remove_party_slot,
)
from src.models.game_save import GameSave, TrainerPartySlot
from src.models.trainer_pokemon import TrainerPokemon
from src.models.user import User
from src.schemas.game_save import GameSaveUpdate


class TestGetGameSave:
    """Tests para get_game_save"""
    
    def test_get_game_save_exists(self, db_session):
        """Obtener partida existente"""
        # Crear trainer
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        # Crear game save
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        result = get_game_save(trainer.id, db_session)
        
        assert result is not None
        assert result.trainer_id == trainer.id
    
    def test_get_game_save_not_exists(self, db_session):
        """Partida no existe - retorna None"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        result = get_game_save(trainer.id, db_session)
        
        assert result is None


class TestGetGameSaveOr404:
    """Tests para get_game_save_or_404"""
    
    def test_get_game_save_or_404_exists(self, db_session):
        """Partida existe - la retorna"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        result = get_game_save_or_404(trainer.id, db_session)
        
        assert result is not None
        assert result.trainer_id == trainer.id
    
    def test_get_game_save_or_404_not_exists(self, db_session):
        """Partida no existe - lanza 404"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            get_game_save_or_404(trainer.id, db_session)
        
        assert exc_info.value.status_code == 404
        assert "partida guardada" in str(exc_info.value.detail).lower()


class TestCreateGameSave:
    """Tests para create_game_save"""
    
    def test_create_game_save_success(self, db_session):
        """Crear partida exitosamente"""
        # Crear trainer
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        # Crear starter pokemon
        pokemon = Mock(id=1)
        starter = TrainerPokemon(
            trainer_id=trainer.id,
            pokemon_id=1,
            is_starter=True,
            is_active=True,
            current_level=5,
            current_experience=0,
            current_hp=100,
            max_hp=100,
            attack=50,
            defense=50,
            sp_attack=50,
            sp_defense=50,
            speed=50,
            known_moves=[],
        )
        db_session.add(starter)
        db_session.commit()
        
        result = create_game_save(trainer.id, db_session)
        
        assert result is not None
        assert result.trainer_id == trainer.id
        
        # Verificar que se creó el slot
        slot = db_session.query(TrainerPartySlot).filter(
            TrainerPartySlot.game_save_id == result.id,
            TrainerPartySlot.slot_position == 0
        ).first()
        assert slot is not None
        assert slot.trainer_pokemon_id == starter.id
    
    def test_create_game_save_already_exists(self, db_session):
        """Ya existe una partida - lanza 409"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            create_game_save(trainer.id, db_session)
        
        assert exc_info.value.status_code == 409
        assert "ya existe" in str(exc_info.value.detail).lower()
    
    def test_create_game_save_no_starter(self, db_session):
        """Trainer sin starter seleccionado - lanza 400"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            create_game_save(trainer.id, db_session)
        
        assert exc_info.value.status_code == 400
        assert "starter" in str(exc_info.value.detail).lower()


class TestUpdateGameSave:
    """Tests para update_game_save"""
    
    def test_update_game_save_success(self, db_session):
        """Actualizar partida exitosamente"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        # CORREGIDO: badges debe ser una lista
        update_data = GameSaveUpdate(badges=["boulder", "cascade"])
        result = update_game_save(trainer.id, update_data, db_session)
        
        assert result.badges == ["boulder", "cascade"]
    
    def test_update_game_save_not_exists(self, db_session):
        """Partida no existe - lanza 404"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        update_data = GameSaveUpdate(badges=["boulder"])
        
        with pytest.raises(HTTPException) as exc_info:
            update_game_save(trainer.id, update_data, db_session)
        
        assert exc_info.value.status_code == 404
    
    def test_update_game_save_partial_update(self, db_session):
        """Actualización parcial - solo algunos campos"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        # CORREGIDO: GameSave no tiene 'location', solo 'badges'
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        # Solo actualizar badges
        update_data = GameSaveUpdate(badges=["cascade"])
        result = update_game_save(trainer.id, update_data, db_session)
        
        assert result.badges == ["cascade"]


class TestSetPartySlot:
    """Tests para set_party_slot"""
    
    def test_set_party_slot_success(self, db_session):
        """Asignar pokémon a slot exitosamente"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        # Crear game save
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        # Crear pokemon del trainer
        pokemon = Mock(id=1)
        trainer_pokemon = TrainerPokemon(
            trainer_id=trainer.id,
            pokemon_id=1,
            is_starter=False,
            is_active=True,
            current_level=5,
            current_experience=0,
            current_hp=100,
            max_hp=100,
            attack=50,
            defense=50,
            sp_attack=50,
            sp_defense=50,
            speed=50,
            known_moves=[],
        )
        db_session.add(trainer_pokemon)
        db_session.commit()
        
        result = set_party_slot(trainer.id, trainer_pokemon.id, 2, db_session)
        
        assert result is not None
        assert result.slot_position == 2
        assert result.trainer_pokemon_id == trainer_pokemon.id
    
    def test_set_party_slot_invalid_position(self, db_session):
        """Posición de slot inválida (<0 o >5) - lanza 400"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            set_party_slot(trainer.id, 1, 6, db_session)
        
        assert exc_info.value.status_code == 400
        assert "slot_position" in str(exc_info.value.detail).lower()
    
    def test_set_party_slot_no_game_save(self, db_session):
        """Trainer sin partida guardada - lanza 404"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            set_party_slot(trainer.id, 1, 1, db_session)
        
        assert exc_info.value.status_code == 404
    
    def test_set_party_slot_pokemon_not_found(self, db_session):
        """Pokémon no pertenece al trainer - lanza 404"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            set_party_slot(trainer.id, 999, 1, db_session)
        
        assert exc_info.value.status_code == 404
    
    def test_set_party_slot_replace_existing(self, db_session):
        """Reemplazar pokémon en slot ya ocupado"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        # Crear dos pokémons
        pokemon1 = TrainerPokemon(
            trainer_id=trainer.id, pokemon_id=1, is_active=True,
            current_level=5, current_experience=0, current_hp=100, max_hp=100,
            attack=50, defense=50, sp_attack=50, sp_defense=50, speed=50, known_moves=[]
        )
        pokemon2 = TrainerPokemon(
            trainer_id=trainer.id, pokemon_id=2, is_active=True,
            current_level=5, current_experience=0, current_hp=100, max_hp=100,
            attack=50, defense=50, sp_attack=50, sp_defense=50, speed=50, known_moves=[]
        )
        db_session.add_all([pokemon1, pokemon2])
        db_session.commit()
        
        # Asignar primer pokémon al slot 1
        set_party_slot(trainer.id, pokemon1.id, 1, db_session)
        
        # Reemplazar con segundo pokémon
        result = set_party_slot(trainer.id, pokemon2.id, 1, db_session)
        
        assert result.trainer_pokemon_id == pokemon2.id
        
        # Verificar que solo hay un slot en posición 1
        slots = db_session.query(TrainerPartySlot).filter(
            TrainerPartySlot.game_save_id == game_save.id,
            TrainerPartySlot.slot_position == 1
        ).all()
        assert len(slots) == 1


class TestRemovePartySlot:
    """Tests para remove_party_slot"""
    
    def test_remove_party_slot_success(self, db_session):
        """Eliminar pokémon de slot exitosamente"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        trainer_pokemon = TrainerPokemon(
            trainer_id=trainer.id, pokemon_id=1, is_active=True,
            current_level=5, current_experience=0, current_hp=100, max_hp=100,
            attack=50, defense=50, sp_attack=50, sp_defense=50, speed=50, known_moves=[]
        )
        db_session.add(trainer_pokemon)
        db_session.commit()
        
        # Crear dos slots para no quedarnos con 0
        slot1 = TrainerPartySlot(game_save_id=game_save.id, trainer_pokemon_id=trainer_pokemon.id, slot_position=0)
        slot2 = TrainerPartySlot(game_save_id=game_save.id, trainer_pokemon_id=trainer_pokemon.id, slot_position=1)
        db_session.add_all([slot1, slot2])
        db_session.commit()
        
        remove_party_slot(trainer.id, 1, db_session)
        
        # Verificar que el slot fue eliminado
        slot = db_session.query(TrainerPartySlot).filter(
            TrainerPartySlot.game_save_id == game_save.id,
            TrainerPartySlot.slot_position == 1
        ).first()
        assert slot is None
    
    def test_remove_party_slot_not_found(self, db_session):
        """Slot no existe - lanza 404"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            remove_party_slot(trainer.id, 5, db_session)
        
        assert exc_info.value.status_code == 404
    
    def test_remove_party_slot_last_pokemon(self, db_session):
        """No permite eliminar el último pokémon de la party - lanza 400"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        game_save = GameSave(trainer_id=trainer.id)
        db_session.add(game_save)
        db_session.commit()
        
        trainer_pokemon = TrainerPokemon(
            trainer_id=trainer.id, pokemon_id=1, is_active=True,
            current_level=5, current_experience=0, current_hp=100, max_hp=100,
            attack=50, defense=50, sp_attack=50, sp_defense=50, speed=50, known_moves=[]
        )
        db_session.add(trainer_pokemon)
        db_session.commit()
        
        # Solo un slot
        slot = TrainerPartySlot(game_save_id=game_save.id, trainer_pokemon_id=trainer_pokemon.id, slot_position=0)
        db_session.add(slot)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            remove_party_slot(trainer.id, 0, db_session)
        
        assert exc_info.value.status_code == 400
        assert "al menos 1" in str(exc_info.value.detail).lower()


# Fixture para db_session
@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.database.database import Base
    
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()