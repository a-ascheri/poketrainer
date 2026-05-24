from datetime import datetime

from pydantic import BaseModel


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
