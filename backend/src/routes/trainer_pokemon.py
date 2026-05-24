from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.user import require_trainer
from src.schemas.pokemon import (
    GainExperienceInput,
    PokemonMovesRead,
    PokemonStatsRead,
    StarterSelectionInput,
    TrainerPokemonRead,
)
from src.services.pokemon_service import (
    acquire_pokemon,
    gain_experience,
    get_trainer_pokemon_moves,
    get_trainer_pokemon_stats,
    list_starters,
    select_starter_pokemon,
)

router = APIRouter(prefix="/trainer", tags=["trainer-pokemon"])


@router.get(
    "/starter/options",
    response_model=list[dict],
    summary="Opciones de starter",
    description="Retorna los 3 pokémon iniciales permitidos para el primer login.",
)
def starter_options_route(
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    starters = list_starters(db)
    return [
        {"id": pokemon.pokeapi_id, "name": pokemon.name, "types": pokemon.types}
        for pokemon in starters
    ]


@router.post(
    "/starter/select",
    response_model=TrainerPokemonRead,
    summary="Seleccionar starter",
    description="Asigna el pokémon inicial al trainer una única vez.",
)
def starter_select_route(
    payload: StarterSelectionInput,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    return select_starter_pokemon(db, trainer, payload.pokemon_name)


@router.post(
    "/pokemon/acquire/{pokeapi_id}",
    response_model=TrainerPokemonRead,
    summary="Adquirir pokemon",
    description="Permite capturar un nuevo pokémon no inicial para el trainer.",
)
def acquire_pokemon_route(
    pokeapi_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    return acquire_pokemon(db, trainer, pokeapi_id)


@router.post(
    "/pokemon/{pokemon_id}/gain-exp",
    response_model=TrainerPokemonRead,
    summary="Sumar experiencia",
    description="Aplica experiencia, recalcula nivel/stats y actualiza movimientos aprendidos.",
)
def gain_exp_route(
    pokemon_id: int,
    payload: GainExperienceInput,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    return gain_experience(db, trainer, pokemon_id, payload.amount)


@router.get(
    "/pokemon/{pokemon_id}/stats",
    response_model=PokemonStatsRead,
    summary="Ver stats actuales",
    description="Obtiene estadísticas de combate del pokémon del trainer.",
)
def stats_route(
    pokemon_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    owned = get_trainer_pokemon_stats(db, trainer, pokemon_id)
    return PokemonStatsRead(
        trainer_pokemon_id=owned.id,
        pokemon_name=owned.pokemon.name,
        current_level=owned.current_level,
        current_experience=owned.current_experience,
        current_hp=owned.current_hp,
        max_hp=owned.max_hp,
        attack=owned.attack,
        defense=owned.defense,
        sp_attack=owned.sp_attack,
        sp_defense=owned.sp_defense,
        speed=owned.speed,
    )


@router.get(
    "/pokemon/{pokemon_id}/moves",
    response_model=PokemonMovesRead,
    summary="Ver movimientos aprendidos",
    description="Devuelve los movimientos disponibles según el nivel actual.",
)
def moves_route(
    pokemon_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    owned = get_trainer_pokemon_moves(db, trainer, pokemon_id)
    return PokemonMovesRead(
        trainer_pokemon_id=owned.id,
        pokemon_name=owned.pokemon.name,
        current_level=owned.current_level,
        known_moves=owned.known_moves,
    )
