from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.routes.auth_dependencies import require_trainer
from src.routes.prefixes import GAME_TRAINER_PREFIX
from src.schemas.pokemon import (GainExperienceInput, PokemonMovesRead,
                                 PokemonStatsRead, StarterSelectionInput,
                                 TrainerPokemonRead)
from src.services.pokemon_service import (acquire_pokemon, gain_experience,
                                          get_trainer_pokemon_moves,
                                          get_trainer_pokemon_stats,
                                          list_starters, list_trainer_pokemon,
                                          select_starter_pokemon)

router = APIRouter(prefix=GAME_TRAINER_PREFIX, tags=["Trainer"])


@router.get(
    "/starter/options",
    response_model=list[dict],
)
def starter_options(
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Devuelve los 3 pokémon iniciales permitidos para el primer login.
    """
    starters = list_starters(db)
    return [
        {
            "id": pokemon.pokeapi_id,
            "name": pokemon.name,
            "types": pokemon.types,
            "imageUrl": pokemon.official_artwork_url
            or f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon.pokeapi_id}.png",
        }
        for pokemon in starters
    ]


@router.post(
    "/starter/select",
    response_model=TrainerPokemonRead,
)
def select_starter(
    payload: StarterSelectionInput,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Asigna el pokémon inicial al trainer una única vez.
    """
    return select_starter_pokemon(db, trainer, payload.pokemon_name)


@router.post(
    "/pokemon/acquire/{pokeapi_id}",
    response_model=TrainerPokemonRead,
)
def acquire_pokemon_for_trainer(
    pokeapi_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Permite capturar un nuevo pokémon no inicial para el trainer.
    """
    return acquire_pokemon(db, trainer, pokeapi_id)


@router.post(
    "/pokemon/{pokemon_id}/gain-exp",
    response_model=TrainerPokemonRead,
)
def gain_experience_for_pokemon(
    pokemon_id: int,
    payload: GainExperienceInput,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Aplica experiencia, recalcula nivel/stats y actualiza movimientos aprendidos.
    """
    return gain_experience(db, trainer, pokemon_id, payload.amount)


@router.get(
    "/pokemon/{pokemon_id}/stats",
    response_model=PokemonStatsRead,
)
def get_pokemon_stats(
    pokemon_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Obtiene estadísticas de combate del pokémon del trainer.
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
def get_pokemon_moves(
    pokemon_id: int,
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Devuelve los movimientos disponibles según el nivel actual del pokémon.
    """
    owned = get_trainer_pokemon_moves(db, trainer, pokemon_id)
    return PokemonMovesRead(
        trainer_pokemon_id=owned.id,
        pokemon_name=owned.pokemon.name,
        current_level=owned.current_level,
        known_moves=owned.known_moves,
    )


@router.get(
    "/pokemon",
    response_model=list[TrainerPokemonRead],
)
def list_my_pokemon(
    db: Session = Depends(get_db),
    trainer=Depends(require_trainer),
):
    """
    Devuelve la lista de pokemones del trainer autenticado.
    """
    return list_trainer_pokemon(db, trainer)
