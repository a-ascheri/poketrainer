# tests/unit/services/test_pokemon_service.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.services.pokemon_service import (
    _experience_to_level,
    _calculate_battle_stats,
    _fetch_json,
    _load_pokemon_payload,
    _load_evolution_chain,
    _extract_moves,
    _extract_evolution_names,
    _known_moves_for_level,
    _build_pokemon_model,
    get_or_create_pokemon,
    list_starters,
    _get_owned_pokemon_or_404,
    _create_owned_pokemon,
    select_starter_pokemon,
    acquire_pokemon,
    gain_experience,
    get_trainer_pokemon_stats,
    get_trainer_pokemon_moves,
    list_trainer_pokemon,
)
from src.models.pokemon import Pokemon
from src.models.trainer_pokemon import TrainerPokemon
from src.models.user import User


class TestExperienceToLevel:
    """Tests para _experience_to_level"""
    
    def test_experience_to_level_growth(self):
        assert _experience_to_level(0) == 1
        assert _experience_to_level(1000) >= 10
        assert _experience_to_level(1000000) <= 100
    
    def test_experience_to_level_negative(self):
        """Cubre línea 21-24: experiencia negativa"""
        assert _experience_to_level(-100) == 1


class TestCalculateBattleStats:
    """Tests para _calculate_battle_stats"""
    
    def test_calculate_stats_returns_required_fields(self):
        stats = _calculate_battle_stats(
            {
                "hp": 45,
                "attack": 49,
                "defense": 49,
                "special-attack": 65,
                "special-defense": 65,
                "speed": 45,
            },
            10,
        )
        
        assert set(stats.keys()) == {
            "max_hp",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "speed",
        }
        assert stats["max_hp"] > 0
    
    def test_calculate_stats_missing_keys(self):
        """Cubre línea 41: stats faltantes usan valores por defecto"""
        stats = _calculate_battle_stats({}, 10)
        assert stats["max_hp"] > 0
        assert stats["attack"] > 0


class TestFetchJson:
    """Tests para _fetch_json"""
    
    @patch("src.services.pokemon_service.requests.get")
    def test_fetch_json_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "bulbasaur"}
        mock_get.return_value = mock_response
        
        result = _fetch_json("https://pokeapi.co/api/v2/pokemon/1")
        
        assert result["id"] == 1
        mock_get.assert_called_once_with("https://pokeapi.co/api/v2/pokemon/1", timeout=12)
    
    @patch("src.services.pokemon_service.requests.get")
    def test_fetch_json_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            _fetch_json("https://pokeapi.co/api/v2/pokemon/fake")
        
        assert exc_info.value.status_code == 404


class TestLoadPokemonPayload:
    """Tests para _load_pokemon_payload"""
    
    @patch("src.services.pokemon_service._fetch_json")
    def test_load_pokemon_payload_new(self, mock_fetch_json):
        """Carga un nuevo Pokémon (cache miss)"""
        mock_fetch_json.return_value = {"id": 25, "name": "pikachu"}
        
        import src.services.pokemon_service as ps
        ps._pokemon_cache.clear()
        
        result = _load_pokemon_payload("pikachu")
        
        assert result["id"] == 25
        assert mock_fetch_json.call_count == 1
    
    @patch("src.services.pokemon_service._fetch_json")
    def test_load_pokemon_payload_cache_hit(self, mock_fetch_json):
        """Segunda llamada usa cache (no llama a fetch_json)"""
        mock_fetch_json.return_value = {"id": 25, "name": "pikachu"}
        
        import src.services.pokemon_service as ps
        ps._pokemon_cache.clear()
        
        result1 = _load_pokemon_payload("pikachu")
        result2 = _load_pokemon_payload("pikachu")
        
        assert result1 == result2
        assert mock_fetch_json.call_count == 1
    
    @patch("src.services.pokemon_service._fetch_json")
    def test_load_pokemon_payload_by_id(self, mock_fetch_json):
        """Carga por ID numérico"""
        mock_fetch_json.return_value = {"id": 25, "name": "pikachu"}
        
        import src.services.pokemon_service as ps
        ps._pokemon_cache.clear()
        
        result = _load_pokemon_payload("25")
        
        assert result["id"] == 25
        mock_fetch_json.assert_called_once_with(f"{ps.POKEAPI_BASE}/pokemon/25")


class TestExtractMoves:
    """Tests para _extract_moves"""
    
    def test_extract_moves_empty(self):
        """Cubre línea 72: payload sin moves"""
        result = _extract_moves({})
        assert result == []
    
    def test_extract_moves_with_data(self):
        payload = {
            "moves": [
                {
                    "move": {"name": "tackle"},
                    "version_group_details": [
                        {
                            "move_learn_method": {"name": "level-up"},
                            "level_learned_at": 1,
                        }
                    ],
                },
                {
                    "move": {"name": "vine-whip"},
                    "version_group_details": [
                        {
                            "move_learn_method": {"name": "level-up"},
                            "level_learned_at": 7,
                        }
                    ],
                },
            ]
        }
        
        result = _extract_moves(payload)
        
        assert len(result) == 2
        assert result[0]["name"] == "tackle"
        assert result[0]["learn_level"] == 1
    
    def test_extract_moves_duplicate_lower_level(self):
        """Test que solo guarda el nivel más bajo para movimientos duplicados"""
        payload = {
            "moves": [
                {
                    "move": {"name": "tackle"},
                    "version_group_details": [
                        {"move_learn_method": {"name": "level-up"}, "level_learned_at": 1},
                        {"move_learn_method": {"name": "level-up"}, "level_learned_at": 5},
                    ],
                },
            ]
        }
        
        result = _extract_moves(payload)
        
        assert result[0]["learn_level"] == 1


class TestExtractEvolutionNames:
    """Tests para _extract_evolution_names"""
    
    def test_extract_evolution_names_empty(self):
        result = _extract_evolution_names({})
        assert result == []
    
    def test_extract_evolution_names_with_chain(self):
        chain = {
            "chain": {
                "species": {"name": "bulbasaur"},
                "evolves_to": [
                    {
                        "species": {"name": "ivysaur"},
                        "evolves_to": [
                            {"species": {"name": "venusaur"}, "evolves_to": []}
                        ],
                    }
                ],
            }
        }
        
        result = _extract_evolution_names(chain)
        
        assert result == ["bulbasaur", "ivysaur", "venusaur"]


class TestKnownMovesForLevel:
    """Tests para _known_moves_for_level"""
    
    def test_known_moves_for_level_empty(self):
        result = _known_moves_for_level([], 10)
        assert result == []
    
    def test_known_moves_for_level_filters_by_level(self):
        moves = [
            {"name": "tackle", "learn_level": 1},
            {"name": "growl", "learn_level": 3},
            {"name": "vine-whip", "learn_level": 7},
            {"name": "razor-leaf", "learn_level": 12},
            {"name": "solar-beam", "learn_level": 20},
        ]
        
        result = _known_moves_for_level(moves, 10)
        
        assert len(result) == 3
        assert result[0]["name"] == "tackle"
        assert result[2]["name"] == "vine-whip"
    
    def test_known_moves_for_level_returns_last_4(self):
        """Solo retorna los últimos 4 movimientos"""
        moves = [
            {"name": "move1", "learn_level": 1},
            {"name": "move2", "learn_level": 2},
            {"name": "move3", "learn_level": 3},
            {"name": "move4", "learn_level": 4},
            {"name": "move5", "learn_level": 5},
        ]
        
        result = _known_moves_for_level(moves, 10)
        
        assert len(result) == 4
        assert result[0]["name"] == "move2"


class TestBuildPokemonModel:
    """Tests para _build_pokemon_model"""
    
    def test_build_pokemon_model(self):
        payload = {
            "id": 1,
            "name": "bulbasaur",
            "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
            "abilities": [{"ability": {"name": "overgrow"}}],
            "stats": [
                {"stat": {"name": "hp"}, "base_stat": 45},
                {"stat": {"name": "attack"}, "base_stat": 49},
            ],
            "moves": [],
        }
        evolution_chain = {"chain": {"species": {"name": "bulbasaur"}, "evolves_to": []}}
        
        result = _build_pokemon_model(payload, evolution_chain)
        
        assert result["pokeapi_id"] == 1
        assert result["name"] == "bulbasaur"
        assert "grass" in result["types"]
        assert "overgrow" in result["abilities"]
        assert result["base_stats"]["hp"] == 45


class TestGetOrCreatePokemon:
    """Tests para get_or_create_pokemon"""
    
    @patch("src.services.pokemon_service._load_pokemon_payload")
    @patch("src.services.pokemon_service._load_evolution_chain")
    @patch("src.services.pokemon_service._build_pokemon_model")
    def test_create_new_pokemon(self, mock_build, mock_evolution, mock_load, db_session):
        mock_load.return_value = {"id": 1, "name": "bulbasaur", "species": {"url": "url"}}
        mock_evolution.return_value = {"chain": {}}
        mock_build.return_value = {
            "pokeapi_id": 1,
            "name": "bulbasaur",
            "types": ["grass"],
            "abilities": ["overgrow"],
            "base_stats": {},
            "moves": [],
            "evolution_chain": {},
            "raw_payload": {},
        }
        
        result = get_or_create_pokemon(db_session, "bulbasaur")
        
        assert result is not None
        assert result.name == "bulbasaur"
    
    @patch("src.services.pokemon_service._load_pokemon_payload")
    def test_get_existing_pokemon(self, mock_load, db_session):
        """Pokémon ya existe en DB"""
        pokemon = Pokemon(pokeapi_id=1, name="bulbasaur", types=[], abilities=[], base_stats={}, moves=[], evolution_chain={})
        db_session.add(pokemon)
        db_session.commit()
        
        mock_load.return_value = {"id": 1, "name": "bulbasaur"}
        
        result = get_or_create_pokemon(db_session, "bulbasaur")
        
        assert result.id == pokemon.id
        assert db_session.query(Pokemon).count() == 1


class TestListStarters:
    """Tests para list_starters"""
    
    @patch("src.services.pokemon_service.get_or_create_pokemon")
    def test_list_starters(self, mock_get_or_create, db_session):
        mock_get_or_create.side_effect = lambda db, name: Pokemon(name=name, pokeapi_id=1)
        
        result = list_starters(db_session)
        
        assert len(result) == 3
        assert mock_get_or_create.call_count == 3


class TestGainExperience:
    """Tests para gain_experience"""
    
    def test_gain_experience_invalid_amount(self, db_session):
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            gain_experience(db_session, trainer, 1, -100)
        
        assert exc_info.value.status_code == 400
    
    def test_gain_experience_level_up(self, db_session):
        """Cubre líneas 233-245: subida de nivel"""
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        pokemon = Pokemon(pokeapi_id=1, name="bulbasaur", types=[], abilities=[], base_stats={}, moves=[], evolution_chain={})
        db_session.add(pokemon)
        db_session.commit()
        
        owned = TrainerPokemon(
            trainer_id=trainer.id,
            pokemon_id=pokemon.id,
            is_starter=True,
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
            is_active=True,
        )
        db_session.add(owned)
        db_session.commit()
        
        result = gain_experience(db_session, trainer, owned.id, 10000)
        
        assert result.current_level > 5
        assert result.current_experience == 10000


class TestGetOwnedPokemonOr404:
    """Tests para _get_owned_pokemon_or_404"""
    
    def test_get_owned_pokemon_not_found(self, db_session):
        trainer = User(username="trainer", email="trainer@test.com", hashed_password="hash")
        db_session.add(trainer)
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            get_trainer_pokemon_stats(db_session, trainer, 999)
        
        assert exc_info.value.status_code == 404


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