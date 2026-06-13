# tests/unit/services/test_pokeapi_service.py

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import HTTPStatusError, RequestError, Request, Response
from src.services.pokeapi_service import (
    get_pokemon_data_from_pokeapi,
    _extract_evolution_names,
    _extract_moves,
    _build_pokemon_image_url,
    pokeapi_cache,
)
from src.schemas.pokemon import PokemonMoveSchema


class TestExtractEvolutionNames:
    """Tests para _extract_evolution_names - línea 23-31"""
    
    def test_extract_evolution_names_simple_chain(self):
        """Cadena de evolución simple"""
        chain = {
            "species": {"name": "bulbasaur"},
            "evolves_to": [
                {
                    "species": {"name": "ivysaur"},
                    "evolves_to": [
                        {"species": {"name": "venusaur"}, "evolves_to": []}
                    ]
                }
            ]
        }
        
        result = _extract_evolution_names(chain)
        
        assert result == ["bulbasaur", "ivysaur", "venusaur"]
    
    def test_extract_evolution_names_no_evolution(self):
        """Pokémon sin evolución"""
        chain = {
            "species": {"name": "lapras"},
            "evolves_to": []
        }
        
        result = _extract_evolution_names(chain)
        
        assert result == ["lapras"]
    
    def test_extract_evolution_names_multiple_branches(self):
        """Múltiples ramas de evolución (Eevee)"""
        chain = {
            "species": {"name": "eevee"},
            "evolves_to": [
                {
                    "species": {"name": "vaporeon"},
                    "evolves_to": []
                },
                {
                    "species": {"name": "jolteon"},
                    "evolves_to": []
                },
                {
                    "species": {"name": "flareon"},
                    "evolves_to": []
                }
            ]
        }
        
        result = _extract_evolution_names(chain)
        
        assert result[0] == "eevee"
        assert set(result[1:]) == {"vaporeon", "jolteon", "flareon"}


class TestExtractMoves:
    """Tests para _extract_moves - línea 36-49"""
    
    def test_extract_moves_empty(self):
        """Sin movimientos"""
        result = _extract_moves([])
        assert result == []
    
    def test_extract_moves_with_level_up(self):
        """Movimientos por nivel"""
        moves_data = [
            {
                "move": {"name": "tackle"},
                "version_group_details": [
                    {
                        "move_learn_method": {"name": "level-up"},
                        "level_learned_at": 1
                    }
                ]
            },
            {
                "move": {"name": "vine-whip"},
                "version_group_details": [
                    {
                        "move_learn_method": {"name": "level-up"},
                        "level_learned_at": 7
                    }
                ]
            }
        ]
        
        result = _extract_moves(moves_data)
        
        assert len(result) == 2
        assert result[0].name == "tackle"
        assert result[0].learnLevel == 1
        assert result[1].name == "vine-whip"
        assert result[1].learnLevel == 7
    
    def test_extract_moves_ignores_non_level_up(self):
        """Ignora movimientos que no son por nivel (TM, huevo, etc.)"""
        moves_data = [
            {
                "move": {"name": "tackle"},
                "version_group_details": [
                    {
                        "move_learn_method": {"name": "level-up"},
                        "level_learned_at": 1
                    }
                ]
            },
            {
                "move": {"name": "hyper-beam"},
                "version_group_details": [
                    {
                        "move_learn_method": {"name": "machine"},
                        "level_learned_at": 0
                    }
                ]
            }
        ]
        
        result = _extract_moves(moves_data)
        
        assert len(result) == 1
        assert result[0].name == "tackle"
    
    def test_extract_moves_takes_lowest_level(self):
        """Cuando un movimiento aparece en múltiples niveles, toma el más bajo"""
        moves_data = [
            {
                "move": {"name": "growl"},
                "version_group_details": [
                    {"move_learn_method": {"name": "level-up"}, "level_learned_at": 3},
                    {"move_learn_method": {"name": "level-up"}, "level_learned_at": 1}
                ]
            }
        ]
        
        result = _extract_moves(moves_data)
        
        assert result[0].learnLevel == 1
    
    def test_extract_moves_limits_to_20(self):
        """Limita a los primeros 20 movimientos"""
        moves_data = []
        for i in range(30):
            moves_data.append({
                "move": {"name": f"move_{i}"},
                "version_group_details": [
                    {"move_learn_method": {"name": "level-up"}, "level_learned_at": i}
                ]
            })
        
        result = _extract_moves(moves_data)
        
        assert len(result) == 20


class TestBuildPokemonImageUrl:
    """Tests para _build_pokemon_image_url - línea 60"""
    
    def test_build_pokemon_image_url(self):
        """Construye URL correcta para la imagen"""
        url = _build_pokemon_image_url(25)
        
        assert url == "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
    
    def test_build_pokemon_image_url_zero(self):
        """ID cero (no debería ocurrir, pero por si acaso)"""
        url = _build_pokemon_image_url(0)
        
        assert "0.png" in url


class TestGetPokemonDataFromPokeapi:
    
    @pytest.mark.asyncio
    async def test_get_pokemon_data_from_cache(self):
        """Usa caché si ya existe - línea 76-80"""
        # Limpiar cache
        pokeapi_cache.clear()
        
        # Primero llenar cache con un mock manual
        from src.schemas.pokemon import PokemonDataResponseSchema, PokemonTypeSchema, PokemonStatSchema
        
        mock_pokemon = PokemonDataResponseSchema(
            id=25,
            name="pikachu",
            height=4,
            weight=60,
            imageUrl="https://example.com/pikachu.png",
            officialArtwork="https://example.com/artwork.png",
            types=[PokemonTypeSchema(name="electric")],
            abilities=["static"],
            moves=[],
            evolutionChain=["pichu", "pikachu", "raichu"],
            stats=[PokemonStatSchema(name="hp", value=35)]
        )
        
        pokeapi_cache["pikachu"] = mock_pokemon
        
        # No debería llamar a la API porque está en cache
        with patch("src.services.pokeapi_service.pokeapi_client") as mock_client:
            result = await get_pokemon_data_from_pokeapi("pikachu")
            
            assert result is not None
            assert result.id == 25
            mock_client.get.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_pokemon_data_404_returns_none(self):
        """Pokémon no encontrado - retorna None (no lanza excepción)"""
        pokeapi_cache.clear()
        
        with patch("src.services.pokeapi_service.pokeapi_client") as mock_client:
            # Simular error 404
            mock_request = Request("GET", "https://pokeapi.co/api/v2/pokemon/fake123")
            mock_response = Response(404, request=mock_request)
            error = HTTPStatusError("Not Found", request=mock_request, response=mock_response)
            mock_client.get.side_effect = error
            
            result = await get_pokemon_data_from_pokeapi("fake123")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_pokemon_data_400_raises_exception(self):
        """Error 400 - Nombre inválido - relanza la excepción"""
        pokeapi_cache.clear()
        
        with patch("src.services.pokeapi_service.pokeapi_client") as mock_client:
            # Simular error 400
            mock_request = Request("GET", "https://pokeapi.co/api/v2/pokemon/ñoño")
            mock_response = Response(400, request=mock_request)
            error = HTTPStatusError("Bad Request", request=mock_request, response=mock_response)
            mock_client.get.side_effect = error
            
            with pytest.raises(HTTPStatusError):
                await get_pokemon_data_from_pokeapi("ñoño")
    
    @pytest.mark.asyncio
    async def test_get_pokemon_data_500_raises_exception(self):
        """Error 500 del servidor - relanza la excepción"""
        pokeapi_cache.clear()
        
        with patch("src.services.pokeapi_service.pokeapi_client") as mock_client:
            # Simular error 500
            mock_request = Request("GET", "https://pokeapi.co/api/v2/pokemon/pikachu")
            mock_response = Response(500, request=mock_request)
            error = HTTPStatusError("Server Error", request=mock_request, response=mock_response)
            mock_client.get.side_effect = error
            
            with pytest.raises(HTTPStatusError):
                await get_pokemon_data_from_pokeapi("pikachu")
    
    @pytest.mark.asyncio
    async def test_get_pokemon_data_request_error(self):
        """Error de red/ conexión - relanza la excepción"""
        pokeapi_cache.clear()
        
        with patch("src.services.pokeapi_service.pokeapi_client") as mock_client:
            error = RequestError("Connection failed", request=None)
            mock_client.get.side_effect = error
            
            with pytest.raises(RequestError):
                await get_pokemon_data_from_pokeapi("pikachu")
    
    @pytest.mark.asyncio
    async def test_get_pokemon_data_unexpected_error(self):
        """Error inesperado - relanza la excepción"""
        pokeapi_cache.clear()
        
        with patch("src.services.pokeapi_service.pokeapi_client") as mock_client:
            mock_client.get.side_effect = Exception("Unexpected error")
            
            with pytest.raises(Exception):
                await get_pokemon_data_from_pokeapi("pikachu")
    
    @pytest.mark.asyncio
    async def test_get_pokemon_data_success_simplified(self):
        """Versión simplificada - cubre transformación de datos y caché"""
        pokeapi_cache.clear()
        
        # Mock simplificado - evitamos AsyncMock anidado
        mock_data = {
            "id": 25,
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "species": {"url": "https://pokeapi.co/api/v2/pokemon-species/25/"},
            "types": [{"type": {"name": "electric"}}],
            "abilities": [{"ability": {"name": "static"}}],
            "moves": [],
            "stats": [
                {"stat": {"name": "hp"}, "base_stat": 35},
                {"stat": {"name": "attack"}, "base_stat": 55},
            ],
            "sprites": {
                "other": {
                    "official-artwork": {
                        "front_default": "https://example.com/artwork.png"
                    }
                }
            }
        }
        
        mock_species_data = {
            "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/25/"}
        }
        
        mock_evolution_data = {
            "chain": {
                "species": {"name": "pichu"},
                "evolves_to": [
                    {
                        "species": {"name": "pikachu"},
                        "evolves_to": [
                            {"species": {"name": "raichu"}, "evolves_to": []}
                        ]
                    }
                ]
            }
        }
        
        # Crear respuestas simuladas como diccionarios simples
        async def mock_get(url):
            class MockResponse:
                def __init__(self, data):
                    self._data = data
                
                def raise_for_status(self):
                    pass
                
                def json(self):
                    return self._data
            
            if "pokemon-species" in url:
                return MockResponse(mock_species_data)
            elif "evolution-chain" in url:
                return MockResponse(mock_evolution_data)
            else:
                return MockResponse(mock_data)
        
        with patch("src.services.pokeapi_service.pokeapi_client") as mock_client:
            mock_client.get = mock_get
            
            result = await get_pokemon_data_from_pokeapi("pikachu")
            
            # Verificaciones
            assert result is not None
            assert result.id == 25
            assert result.name == "pikachu"
            assert result.height == 4
            assert result.weight == 60
            assert len(result.types) == 1
            assert result.types[0].name == "electric"
            assert "static" in result.abilities
            assert len(result.evolutionChain) == 3
            assert result.evolutionChain[0] == "pichu"
            
            # Verificar que se guardó en caché
            assert "pikachu" in pokeapi_cache
            assert pokeapi_cache["pikachu"].id == 25
    
    @pytest.mark.asyncio
    async def test_get_pokemon_data_normalizes_query_simplified(self):
        """Versión simplificada - cubre normalización de query"""
        pokeapi_cache.clear()
        
        mock_data = {
            "id": 25,
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "species": {"url": "https://pokeapi.co/api/v2/pokemon-species/25/"},
            "types": [],
            "abilities": [],
            "moves": [],
            "stats": [],
            "sprites": {"other": {"official-artwork": {"front_default": ""}}}
        }
        
        mock_species_data = {
            "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/25/"}
        }
        
        mock_evolution_data = {"chain": {"species": {"name": "pikachu"}, "evolves_to": []}}
        
        # Contador para verificar que solo se llama una vez (por la caché)
        call_count = 0
        
        async def mock_get(url):
            nonlocal call_count
            call_count += 1
            
            class MockResponse:
                def __init__(self, data):
                    self._data = data
                
                def raise_for_status(self):
                    pass
                
                def json(self):
                    return self._data
            
            if "pokemon-species" in url:
                return MockResponse(mock_species_data)
            elif "evolution-chain" in url:
                return MockResponse(mock_evolution_data)
            else:
                return MockResponse(mock_data)
        
        with patch("src.services.pokeapi_service.pokeapi_client") as mock_client:
            mock_client.get = mock_get
            
            # Primera llamada con mayúsculas y espacios
            result1 = await get_pokemon_data_from_pokeapi("  PIKACHU  ")
            
            # Segunda llamada (debería usar caché)
            result2 = await get_pokemon_data_from_pokeapi("pikachu")
            
            # Verificaciones
            assert result1 is not None
            assert result1.name == "pikachu"
            assert result2 is not None
            assert result2.name == "pikachu"
            
            # Verificar que la API solo se llamó una vez (la segunda vez usó caché)
            # Nota: 3 llamadas por cada request (pokemon, species, evolution)
            assert call_count == 3
            
            # Verificar que se guardó en caché con la clave normalizada
            assert "pikachu" in pokeapi_cache


# Limpiar cache después de cada test
@pytest.fixture(autouse=True)
def clear_cache():
    """Limpia la caché antes de cada test"""
    pokeapi_cache.clear()
    yield
    pokeapi_cache.clear()