from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.user import require_trainer
from src.schemas.pokemon import (GainExperienceInput, PokemonMovesRead,
                                 PokemonStatsRead, StarterSelectionInput,
                                 TrainerPokemonRead)
from src.services.pokemon_service import (acquire_pokemon, gain_experience,
                                          get_trainer_pokemon_moves,
                                          get_trainer_pokemon_stats,
                                          list_starters,
                                          select_starter_pokemon)

router = APIRouter(prefix="/trainer", tags=["Trainer-Pokemon"])


@router.get(
    "/starter/options",
    response_model=list[dict],
)
def starter_options_route(
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Devuelve los 3 pokémon iniciales permitidos para el primer login.

    Args:
        db (Session): Sesión de base de datos.
        trainer: Trainer autenticado.

    Returns:
        list[dict]: Lista de pokémon iniciales.
    """
    starters = list_starters(db)
    return [
        {"id": pokemon.pokeapi_id, "name": pokemon.name, "types": pokemon.types}
        for pokemon in starters
    ]


@router.post(
    "/starter/select",
    response_model=TrainerPokemonRead,
)
def starter_select_route(
    payload: StarterSelectionInput,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Asigna el pokémon inicial al trainer una única vez.

    Args:
        payload (StarterSelectionInput): Selección del pokémon inicial.
        db (Session): Sesión de base de datos.
        trainer: Trainer autenticado.

    Returns:
        TrainerPokemonRead: Pokémon inicial asignado.
    """
    return select_starter_pokemon(db, trainer, payload.pokemon_name)


@router.post(
    "/pokemon/acquire/{pokeapi_id}",
    response_model=TrainerPokemonRead,
)
def acquire_pokemon_route(
    pokeapi_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Permite capturar un nuevo pokémon no inicial para el trainer.

    Args:
        pokeapi_id (int): ID del pokémon a capturar.
        db (Session): Sesión de base de datos.
        trainer: Trainer autenticado.

    Returns:
        TrainerPokemonRead: Pokémon capturado.
    """
    return acquire_pokemon(db, trainer, pokeapi_id)


@router.post(
    "/pokemon/{pokemon_id}/gain-exp",
    response_model=TrainerPokemonRead,
)
def gain_exp_route(
    pokemon_id: int,
    payload: GainExperienceInput,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Aplica experiencia, recalcula nivel/stats y actualiza movimientos aprendidos.

    Args:
        pokemon_id (int): ID del pokémon a actualizar.
        payload (GainExperienceInput): Cantidad de experiencia a sumar.
        db (Session): Sesión de base de datos.
        trainer: Trainer autenticado.

    Returns:
        TrainerPokemonRead: Pokémon actualizado.
    """
    return gain_experience(db, trainer, pokemon_id, payload.amount)


@router.get(
    "/pokemon/{pokemon_id}/stats",
    response_model=PokemonStatsRead,
)
def stats_route(
    pokemon_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Obtiene estadísticas de combate del pokémon del trainer.

    Args:
        pokemon_id (int): ID del pokémon.
        db (Session): Sesión de base de datos.
        trainer: Trainer autenticado.

    Returns:
        PokemonStatsRead: Estadísticas del pokémon.
    """
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
)
def moves_route(
    pokemon_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Devuelve los movimientos disponibles según el nivel actual del pokémon.

    Args:
        pokemon_id (int): ID del pokémon.
        db (Session): Sesión de base de datos.
        trainer: Trainer autenticado.

    Returns:
        PokemonMovesRead: Movimientos aprendidos del pokémon.
    """
    owned = get_trainer_pokemon_moves(db, trainer, pokemon_id)
    return PokemonMovesRead(
        trainer_pokemon_id=owned.id,
        pokemon_name=owned.pokemon.name,
        current_level=owned.current_level,
        known_moves=owned.known_moves,
    )
