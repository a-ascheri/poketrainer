from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.prefixes import POKEMON_PREFIX
from src.schemas.pokemon import PokemonDataResponseSchema, PokemonSearchInput
from src.services.pokeapi_service import get_pokemon_data_from_pokeapi


router = APIRouter(prefix=POKEMON_PREFIX, tags=["Pokemon"])


@router.get(
    "/{query}",
    response_model=PokemonDataResponseSchema,
    summary="Buscar Pokémon por nombre o ID",
    description="Obtiene datos de un Pokémon, consultando la PokeAPI a través del backend con cacheo.",
)
# Aunque no interactúa con DB local directamente, se mantiene para consistencia
async def search_pokemon(
    query: str,
    db: Session = Depends(
        get_db
    ),  
) -> PokemonDataResponseSchema:
    """
    Endpoint para buscar un Pokémon por su nombre o ID.
    Los datos se obtienen de PokeAPI y se gestionan a través del servicio con cacheo.
    """
    # Usamos el schema para validar y limpiar la query
    search_input = PokemonSearchInput(query=query)
    validated_query = search_input.query

    pokemon_data = await get_pokemon_data_from_pokeapi(validated_query)

    if not pokemon_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pokémon '{validated_query}' no encontrado.",
        )

    return pokemon_data
