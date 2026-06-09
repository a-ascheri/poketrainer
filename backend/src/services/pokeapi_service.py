import httpx
from typing import List, Dict, Any, Optional

from src.schemas.pokemon import (
    PokemonDataResponseSchema,
    PokemonTypeSchema,
    PokemonStatSchema,
    PokemonMoveSchema,
)

# --- Configuración de PokeAPI ---
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
# Usaremos un cliente httpx para peticiones asíncronas
pokeapi_client = httpx.AsyncClient(base_url=POKEAPI_BASE_URL)

# --- Cache en memoria simple (Para empezar, luego se puede integrar Redis) ---
# Ojo: No es escalable si hay múltiples instancias del backend
# y no persiste si el servidor se reinicia. Solo para demo/desarrollo inicial.
pokeapi_cache: Dict[str, PokemonDataResponseSchema] = {}
CACHE_TTL_SECONDS = 3600  # 1 hora

# --- Funciones de Transformación (Adaptadas del Frontend) ---

def _extract_evolution_names(chain: Dict[str, Any]) -> List[str]:
    """Extrae los nombres de la cadena de evolución de la respuesta de PokeAPI."""
    names: List[str] = []

    def walk(node: Dict[str, Any]):
        names.append(node["species"]["name"])
        for next_node in node.get("evolves_to", []):
            walk(next_node)

    walk(chain)
    return names

def _extract_moves(moves_data: List[Dict[str, Any]]) -> List[PokemonMoveSchema]:
    """Extrae y filtra los movimientos por nivel de aprendizaje de la respuesta de PokeAPI."""
    registry = {} # type: Dict[str, int]

    for entry in moves_data:
        move_name = entry["move"]["name"]
        for detail in entry.get("version_group_details", []):
            if detail["move_learn_method"]["name"] != "level-up":
                continue
            learn_level = detail["level_learned_at"]
            if move_name not in registry or learn_level < registry[move_name]:
                registry[move_name] = learn_level
    
    # Convertir el registro a una lista de PokemonMoveSchema y ordenar
    # Limitar a los primeros 20 movimientos como en el frontend original
    return sorted(
        [PokemonMoveSchema(name=name, learnLevel=level) for name, level in registry.items()],
        key=lambda x: x.learnLevel
    )[:20]

def _build_pokemon_image_url(pokemon_id: int) -> str:
    """Construye la URL de la imagen sprite del Pokémon."""
    return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png"

# --- Función Principal para Obtener Datos de Pokémon ---

async def get_pokemon_data_from_pokeapi(query: str) -> Optional[PokemonDataResponseSchema]:
    """
    Obtiene y procesa datos de un Pokémon de la PokeAPI, con cacheo.
    Busca por nombre o ID.
    """
    normalized_query = query.strip().lower()

    # 1. Intentar obtener de la caché
    if normalized_query in pokeapi_cache:
        # Aquí se podría añadir lógica de TTL para la caché
        # Por ahora, simplemente devolvemos si está en caché
        return pokeapi_cache[normalized_query]

    try:
        # 2. Realizar la primera llamada a PokeAPI para datos básicos
        response = await pokeapi_client.get(f"/pokemon/{normalized_query}")
        response.raise_for_status() # Lanza excepción para códigos de estado 4xx/5xx
        data = response.json()

        # 3. Llamada para datos de la especie (para la cadena de evolución)
        species_response = await pokeapi_client.get(data["species"]["url"])
        species_response.raise_for_status()
        species_data = species_response.json()

        # 4. Llamada para la cadena de evolución
        evolution_response = await pokeapi_client.get(species_data["evolution_chain"]["url"])
        evolution_response.raise_for_status()
        evolution_data = evolution_response.json()

        # 5. Transformar los datos al formato de PokemonDataResponseSchema
        pokemon_id = data["id"]
        processed_pokemon = PokemonDataResponseSchema(
            id=pokemon_id,
            name=data["name"],
            height=data["height"],
            weight=data["weight"],
            imageUrl=_build_pokemon_image_url(pokemon_id),
            officialArtwork=data["sprites"]["other"]["official-artwork"]["front_default"] or "",
            types=[PokemonTypeSchema(name=entry["type"]["name"]) for entry in data["types"]],
            abilities=[entry["ability"]["name"] for entry in data["abilities"]],
            moves=_extract_moves(data["moves"]),
            evolutionChain=_extract_evolution_names(evolution_data["chain"]),
            stats=[
                PokemonStatSchema(name=entry["stat"]["name"], value=entry["base_stat"])
                for entry in data["stats"]
            ],
        )

        # 6. Almacenar en la caché antes de devolver
        pokeapi_cache[normalized_query] = processed_pokemon
        return processed_pokemon

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"Pokémon '{query}' no encontrado en PokeAPI.")
            return None
        print(f"Error HTTP al consultar PokeAPI para '{query}': {e}")
        raise # Re-lanzar otros errores HTTP
    except httpx.RequestError as e:
        print(f"Error de red al consultar PokeAPI para '{query}': {e}")
        raise # Re-lanzar errores de red
    except Exception as e:
        print(f"Error inesperado al procesar datos de PokeAPI para '{query}': {e}")
        raise # Re-lanzar cualquier otro error inesperado
