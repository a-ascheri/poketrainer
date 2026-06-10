from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session
from pydantic import ValidationError

from src.database.database import get_db
from src.routes.prefixes import POKEMON_PREFIX
from src.schemas.pokemon import PokemonDataResponseSchema, PokemonSearchInput
from src.services.pokeapi_service import get_pokemon_data_from_pokeapi

router = APIRouter(prefix=POKEMON_PREFIX, tags=["Pokemon"])


@router.get(
    "/{query_param}",
    response_model=PokemonDataResponseSchema,
    summary="Buscar Pokémon por nombre o ID",
    description="Obtiene datos de un Pokémon, consultando la PokeAPI a través del backend con cacheo.",
)
# Aunque no interactúa con DB local directamente, se mantiene para consistencia
async def search_pokemon(
    query_param: str = Path(..., description="Nombre o ID del Pokémon a buscar", example="pikachu"), # <-- Usar Path
    db: Session = Depends(get_db),
) -> PokemonDataResponseSchema:
    """
    Endpoint para buscar un Pokémon por su nombre o ID.
    Los datos se obtienen de PokeAPI y se gestionan a través del servicio con cacheo.
    """
    try:
        # 1. Validar la query usando nuestro schema Pydantic
        # Si la validación falla, Pydantic/FastAPI automáticamente generará un 422
        search_input = PokemonSearchInput(query=query_param)
        validated_query = search_input.query

        # 2. Llamar al servicio con la query validada
        pokemon_data = await get_pokemon_data_from_pokeapi(validated_query)

        if not pokemon_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pokémon '{validated_query}' no encontrado."
            )

        return pokemon_data

    except ValidationError as e:
    # Convertir los errores de Pydantic a un formato JSON serializable
        errors = []
        for error in e.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "input": error.get("input")
            })
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Error de validación en la búsqueda",
                "errors": errors
            }
        )
    except Exception as e:
        # Captura cualquier otra excepción inesperada
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error inesperado en el servidor: {e}"
        )
