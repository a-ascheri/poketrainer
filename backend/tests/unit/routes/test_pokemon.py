import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.main import app

client = TestClient(app)


class TestSearchPokemon:
    """Tests para el endpoint GET /api/v1/pokemon/{query_param}"""

    def test_search_pokemon_by_name_success(self):
        """Caso feliz: buscar por nombre existente"""
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_pokeapi.return_value = {
                "id": 25,
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "imageUrl": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
                "officialArtwork": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
                "types": [{"name": "electric"}],
                "abilities": ["static"],
                "moves": [
                    {"name": "thunder-shock", "learnLevel": 1},
                    {"name": "quick-attack", "learnLevel": 5},
                ],
                "evolutionChain": ["pichu", "pikachu", "raichu"],
                "stats": [
                    {"name": "hp", "value": 35},
                    {"name": "attack", "value": 55},
                    {"name": "defense", "value": 40},
                    {"name": "special-attack", "value": 50},
                    {"name": "special-defense", "value": 50},
                    {"name": "speed", "value": 90},
                ],
            }
            
            response = client.get("/api/v1/pokemon/pikachu")
            
            assert response.status_code == 200
            assert response.json()["name"] == "pikachu"
            assert response.json()["id"] == 25
            assert len(response.json()["types"]) == 1
            assert response.json()["types"][0]["name"] == "electric"
            assert len(response.json()["moves"]) == 2
            mock_pokeapi.assert_called_once_with("pikachu")

    def test_search_pokemon_by_id_success(self):
        """Buscar por ID existente"""
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_pokeapi.return_value = {
                "id": 1,
                "name": "bulbasaur",
                "height": 7,
                "weight": 69,
                "imageUrl": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
                "officialArtwork": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png",
                "types": [{"name": "grass"}, {"name": "poison"}],
                "abilities": ["overgrow"],
                "moves": [
                    {"name": "tackle", "learnLevel": 1},
                    {"name": "growl", "learnLevel": 3},
                ],
                "evolutionChain": ["bulbasaur", "ivysaur", "venusaur"],
                "stats": [
                    {"name": "hp", "value": 45},
                    {"name": "attack", "value": 49},
                    {"name": "defense", "value": 49},
                    {"name": "special-attack", "value": 65},
                    {"name": "special-defense", "value": 65},
                    {"name": "speed", "value": 45},
                ],
            }
            
            response = client.get("/api/v1/pokemon/1")
            
            assert response.status_code == 200
            assert response.json()["id"] == 1
            assert response.json()["name"] == "bulbasaur"
            assert len(response.json()["types"]) == 2
            mock_pokeapi.assert_called_once_with("1")

    def test_search_pokemon_not_found_404(self):
        """Pokémon no existe en PokeAPI"""
        from httpx import HTTPStatusError, Request, Response
        
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_request = Request("GET", "https://pokeapi.co/api/v2/pokemon/fake123")
            mock_response = Response(404, request=mock_request)
            mock_pokeapi.side_effect = HTTPStatusError(
                "Not Found", request=mock_request, response=mock_response
            )
            
            response = client.get("/api/v1/pokemon/fake123")
            
            assert response.status_code == 404
            assert "no encontrado" in response.json()["detail"].lower()

    def test_search_pokemon_invalid_name_400(self):
        """Nombre inválido con caracteres especiales"""
        from httpx import HTTPStatusError, Request, Response
        
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_request = Request("GET", "https://pokeapi.co/api/v2/pokemon/ñoño")
            mock_response = Response(400, request=mock_request)
            mock_pokeapi.side_effect = HTTPStatusError(
                "Bad Request", request=mock_request, response=mock_response
            )
            
            response = client.get("/api/v1/pokemon/ñoño")
            
            assert response.status_code == 400
            assert "inválido" in response.json()["detail"]

    def test_search_pokemon_negative_id_422(self):
        """ID negativo - debe fallar validación Pydantic"""
        response = client.get("/api/v1/pokemon/-5")
        
        assert response.status_code == 422
        assert "validación" in response.json()["detail"]["message"].lower()

    def test_search_pokemon_zero_id_422(self):
        """ID cero - debe fallar validación"""
        response = client.get("/api/v1/pokemon/0")
        
        assert response.status_code == 422

    def test_search_pokemon_id_too_large_422(self):
        """ID muy grande (mayor a 9999) - debe fallar validación"""
        response = client.get("/api/v1/pokemon/10000")
        
        assert response.status_code == 422

    def test_search_pokemon_special_characters_422(self):
        """Caracteres especiales no permitidos"""
        response = client.get("/api/v1/pokemon/pika@chu")
        
        assert response.status_code == 422

    def test_search_pokemon_empty_response(self):
        """El servicio retorna None - esto no debería ocurrir porque get_pokemon_data_from_pokeapi siempre retorna dict o lanza excepción"""
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_pokeapi.return_value = None
            
            response = client.get("/api/v1/pokemon/pikachu")
            
            # El código lanza HTTPException(404) cuando pokemon_data es None
            assert response.status_code == 404
            assert "no encontrado" in response.json()["detail"].lower()

    def test_search_pokemon_connection_error_503(self):
        """Error de conexión con PokeAPI"""
        from httpx import RequestError
        
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_pokeapi.side_effect = RequestError("Connection failed", request=None)
            
            response = client.get("/api/v1/pokemon/pikachu")
            
            assert response.status_code == 503
            assert "conectar" in response.json()["detail"].lower()

    def test_search_pokemon_unexpected_error_500(self):
        """Error inesperado del servidor"""
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_pokeapi.side_effect = Exception("Unexpected database error")
            
            response = client.get("/api/v1/pokemon/pikachu")
            
            assert response.status_code == 500
            assert "inesperado" in response.json()["detail"].lower()

    def test_search_pokemon_pokeapi_502_error(self):
        """PokeAPI devuelve error 502 (Bad Gateway)"""
        from httpx import HTTPStatusError, Request, Response
        
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_request = Request("GET", "https://pokeapi.co/api/v2/pokemon/pikachu")
            mock_response = Response(502, request=mock_request)
            mock_pokeapi.side_effect = HTTPStatusError(
                "Bad Gateway", request=mock_request, response=mock_response
            )
            
            response = client.get("/api/v1/pokemon/pikachu")
            
            assert response.status_code == 502
            assert "PokeAPI" in response.json()["detail"]

    def test_search_pokemon_pokeapi_418_error(self):
        """PokeAPI devuelve error 418 (I'm a teapot) - cubre el else del HTTPStatusError"""
        from httpx import HTTPStatusError, Request, Response
        
        with patch("src.routes.pokemon.get_pokemon_data_from_pokeapi", new_callable=AsyncMock) as mock_pokeapi:
            mock_request = Request("GET", "https://pokeapi.co/api/v2/pokemon/pikachu")
            mock_response = Response(418, request=mock_request)
            mock_pokeapi.side_effect = HTTPStatusError(
                "I'm a teapot", request=mock_request, response=mock_response
            )
            
            response = client.get("/api/v1/pokemon/pikachu")
            
            # 418 no está manejado específicamente, va al else que da 502
            assert response.status_code == 502
            assert "PokeAPI" in response.json()["detail"]


# Configuración para async tests
@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()