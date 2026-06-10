import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class PokemonRead(BaseModel):
    id: int
    pokeapi_id: int
    name: str
    types: list[str]
    abilities: list[str]
    base_stats: dict[str, int]
    moves: list[dict]
    evolution_chain: dict | None = None

    class Config:
        from_attributes = True


class StarterSelectionInput(BaseModel):
    pokemon_name: str


class GainExperienceInput(BaseModel):
    amount: int


class TrainerPokemonRead(BaseModel):
    id: int
    trainer_id: int
    pokemon: PokemonRead
    is_starter: bool
    current_level: int
    current_experience: int
    current_hp: int
    max_hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    known_moves: list[dict]
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class PokemonStatsRead(BaseModel):
    trainer_pokemon_id: int
    pokemon_name: str
    current_level: int
    current_experience: int
    current_hp: int
    max_hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int


class PokemonMovesRead(BaseModel):
    trainer_pokemon_id: int
    pokemon_name: str
    current_level: int
    known_moves: list[dict]


# Schemas para la Lógica de PokeAPI a Backend
class PokemonTypeSchema(BaseModel):
    name: str = Field(..., description="Nombre del tipo de Pokémon")


class PokemonStatSchema(BaseModel):
    name: str = Field(..., description="Nombre de la estadística (HP, attack, etc.)")
    value: int = Field(..., ge=0, description="Valor base de la estadística")


class PokemonMoveSchema(BaseModel):
    name: str = Field(..., description="Nombre del movimiento")
    learnLevel: int = Field(
        ..., ge=0, description="Nivel en el que se aprende el movimiento"
    )


class PokemonDataResponseSchema(BaseModel):
    """
    Schema para la respuesta de datos de Pokémon procesados para el frontend,
    basado en la estructura que el frontend esperaba de la PokeAPI.
    """

    id: int = Field(..., ge=1, description="ID numérico del Pokémon en la PokeAPI")
    name: str = Field(..., min_length=1, description="Nombre del Pokémon")
    height: int = Field(..., ge=0, description="Altura del Pokémon en decímetros")
    weight: int = Field(..., ge=0, description="Peso del Pokémon en hectogramos")
    imageUrl: str = Field(..., description="URL de la imagen sprite del Pokémon")
    officialArtwork: str = Field(..., description="URL del arte oficial del Pokémon")
    types: List[PokemonTypeSchema] = Field(
        ..., description="Lista de tipos del Pokémon"
    )
    abilities: List[str] = Field(
        ..., description="Lista de nombres de habilidades del Pokémon"
    )
    moves: List[PokemonMoveSchema] = Field(
        ..., description="Lista de movimientos que el Pokémon puede aprender"
    )
    evolutionChain: List[str] = Field(
        ..., description="Nombres de la cadena de evolución del Pokémon"
    )
    stats: List[PokemonStatSchema] = Field(
        ..., description="Lista de estadísticas base del Pokémon"
    )

    class Config:
        from_attributes = True


class PokemonSearchInput(BaseModel):
    """
    Schema para validar el parámetro de búsqueda de Pokémon.
    Añade validaciones para números negativos y formato de texto.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre o ID del Pokémon a buscar",
        example="pikachu",
    )

    @validator("query")
    def validate_query_content(cls, v):
        stripped_query = v.strip()
        if not stripped_query:
            raise ValueError(
                "La consulta de búsqueda no puede estar vacía o consistir solo en espacios."
            )

        # Validación para números negativos o cero si la consulta es un número (ID de Pokémon)
        if stripped_query.isdigit():
            pokemon_id = int(stripped_query)
            if pokemon_id <= 0:
                raise ValueError("El ID del Pokémon no puede ser cero o negativo.")

        # Validación con Expresiones Regulares (ej. para nombres)
        # La regex actual permite letras (unicode), números, espacios, guiones y apóstrofes.
        if not re.fullmatch(r"[\w\s\-\']+", stripped_query, re.UNICODE):
            raise ValueError(
                "La consulta contiene caracteres no permitidos. "
                "Usa solo letras, números, espacios, guiones y apóstrofes."
            )

        return stripped_query
