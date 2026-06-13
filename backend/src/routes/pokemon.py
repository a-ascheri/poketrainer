from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.prefixes import POKEMON_PREFIX
from src.schemas.pokemon import PokemonDataResponseSchema, PokemonSearchInput
from src.services.pokeapi_service import get_pokemon_data_from_pokeapi

router = APIRouter(prefix=POKEMON_PREFIX, tags=["Pokemon"])


@router.get(
    "/{query_param}",
    response_model=PokemonDataResponseSchema,
)
async def search_pokemon(
    query_param: str = Path(
        ..., description="Nombre o ID del Pokémon a buscar", example="pikachu"
    ),
    db: Session = Depends(get_db),
) -> PokemonDataResponseSchema:
    """
    Endpoint para buscar un Pokémon por nombre o ID. Valida la entrada usando Pydantic y maneja errores específicos de PokeAPI.

    Args:
        query_param (str, optional): _description_. Defaults to Path( ..., description="Nombre o ID del Pokémon a buscar", example="pikachu" ).
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_ se lanza cuando la validación de Pydantic falla, con detalles de los errores de validación.
        HTTPException: _description_ se lanza cuando PokeAPI devuelve un error HTTP, con detalles específicos según el código de estado.
        HTTPException: _description_ se lanza cuando PokeAPI devuelve un error de red o conexión.
        HTTPException: _description_ se lanza cuando ocurre un error inesperado en PokeAPI.
        HTTPException: _description_ se lanza cuando el Pokémon no se encuentra.
        HTTPException: _description_ se lanza cuando ocurre un error interno del servidor.
        HTTPException: _description_ se lanza cuando ocurre un error desconocido.

    Returns:
        PokemonDataResponseSchema: _description_
    """
    try:
        # 1. Validar la query usando schema Pydantic
        search_input = PokemonSearchInput(query=query_param)
        validated_query = search_input.query

        # 2. Llamar al servicio con la query validada
        pokemon_data = await get_pokemon_data_from_pokeapi(validated_query)

        if not pokemon_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pokémon '{validated_query}' no encontrado.",
            )

        return pokemon_data

    except ValidationError as e:
        # Validación de Pydantic falló
        errors = []
        for error in e.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "input": error.get("input"),
                }
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Error de validación en la búsqueda", "errors": errors},
        )
    
    except httpx.HTTPStatusError as e:
        # Error HTTP de PokeAPI
        print(f"HTTPStatusError capturado: {e.response.status_code} para '{query_param}'")
        if e.response.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nombre de Pokémon inválido: '{query_param}'. Usa solo letras, números, guiones o apóstrofes."
            )
        elif e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pokémon '{query_param}' no encontrado."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error de PokeAPI: {e.response.status_code}"
            )
    
    except httpx.RequestError as e:
        print(f"RequestError capturado: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con PokeAPI. Intenta más tarde."
        )
    
    except HTTPException:
        # Relanzar HTTPException para que FastAPI las maneje correctamente
        raise
    
    except Exception as e:
        # Cualquier otro error inesperado
        print(f"Error inesperado: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado en el servidor."
        )