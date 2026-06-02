from __future__ import annotations

from datetime import datetime, timezone

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.pokemon import Pokemon
from src.models.trainer_pokemon import TrainerPokemon
from src.models.user import User

POKEAPI_BASE = "https://pokeapi.co/api/v2"
STARTER_NAMES = {"bulbasaur", "charmander", "squirtle"}

_pokemon_cache: dict[str, dict] = {}
_evolution_cache: dict[str, dict] = {}


def _fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=12)
    if response.status_code >= 400:
        raise HTTPException(status_code=404, detail="Pokemon data not found")
    return response.json()


def _load_pokemon_payload(query: str) -> dict:
    normalized = str(query).strip().lower()
    if normalized in _pokemon_cache:
        return _pokemon_cache[normalized]

    payload = _fetch_json(f"{POKEAPI_BASE}/pokemon/{normalized}")
    _pokemon_cache[normalized] = payload
    _pokemon_cache[str(payload["id"])] = payload
    _pokemon_cache[payload["name"]] = payload
    return payload


def _load_evolution_chain(species_url: str) -> dict:
    if species_url in _evolution_cache:
        return _evolution_cache[species_url]

    species_payload = _fetch_json(species_url)
    evolution_url = species_payload["evolution_chain"]["url"]
    evolution_payload = _fetch_json(evolution_url)
    _evolution_cache[species_url] = evolution_payload
    return evolution_payload


def _extract_moves(payload: dict) -> list[dict]:
    collected: dict[str, int] = {}
    for move_entry in payload.get("moves", []):
        move_name = move_entry["move"]["name"]
        for details in move_entry.get("version_group_details", []):
            if details.get("move_learn_method", {}).get("name") != "level-up":
                continue
            level = details.get("level_learned_at", 0)
            if move_name not in collected or level < collected[move_name]:
                collected[move_name] = level

    return [
        {"name": name, "learn_level": level}
        for name, level in sorted(collected.items(), key=lambda item: item[1])
    ]


def _extract_evolution_names(chain: dict) -> list[str]:
    names: list[str] = []

    def _walk(node: dict):
        if not node:
            return
        species_name = node.get("species", {}).get("name")
        if species_name:
            names.append(species_name)
        for child in node.get("evolves_to", []):
            _walk(child)

    _walk(chain.get("chain", {}))
    return names


def _experience_to_level(experience: int) -> int:
    if experience <= 0:
        return 1
    estimated = int(experience ** (1 / 3)) + 1
    return min(max(estimated, 1), 100)


def _calculate_battle_stats(base_stats: dict[str, int], level: int) -> dict[str, int]:
    hp = int(((2 * base_stats.get("hp", 45)) * level) / 100) + level + 10

    def _formula(stat_name: str) -> int:
        return int(((2 * base_stats.get(stat_name, 45)) * level) / 100) + 5

    return {
        "max_hp": hp,
        "attack": _formula("attack"),
        "defense": _formula("defense"),
        "sp_attack": _formula("special-attack"),
        "sp_defense": _formula("special-defense"),
        "speed": _formula("speed"),
    }


def _known_moves_for_level(moves: list[dict], level: int) -> list[dict]:
    available = [move for move in moves if move.get("learn_level", 0) <= level]
    return available[-4:]


def _build_pokemon_model(payload: dict, evolution_chain: dict) -> dict:
    base_stats = {
        stat["stat"]["name"]: stat["base_stat"] for stat in payload.get("stats", [])
    }
    return {
        "pokeapi_id": payload["id"],
        "name": payload["name"],
        "types": [entry["type"]["name"] for entry in payload.get("types", [])],
        "abilities": [
            entry["ability"]["name"] for entry in payload.get("abilities", [])
        ],
        "base_stats": base_stats,
        "moves": _extract_moves(payload),
        "evolution_chain": {
            "names": _extract_evolution_names(evolution_chain),
            "raw": evolution_chain,
        },
        "raw_payload": payload,
    }


def get_or_create_pokemon(db: Session, query: str) -> Pokemon:
    payload = _load_pokemon_payload(query)

    existing = db.query(Pokemon).filter(Pokemon.pokeapi_id == payload["id"]).first()
    if existing:
        return existing

    species_url = payload.get("species", {}).get("url")
    evolution_chain = (
        _load_evolution_chain(species_url) if species_url else {"chain": {}}
    )

    model_data = _build_pokemon_model(payload, evolution_chain)
    pokemon = Pokemon(**model_data)
    db.add(pokemon)
    db.commit()
    db.refresh(pokemon)
    return pokemon


def list_starters(db: Session) -> list[Pokemon]:
    starters: list[Pokemon] = []
    for name in sorted(STARTER_NAMES):
        starters.append(get_or_create_pokemon(db, name))
    return starters


def _get_owned_pokemon_or_404(
    db: Session, trainer_id: int, trainer_pokemon_id: int
) -> TrainerPokemon:
    owned = (
        db.query(TrainerPokemon)
        .filter(
            TrainerPokemon.id == trainer_pokemon_id,
            TrainerPokemon.trainer_id == trainer_id,
            TrainerPokemon.deleted_at.is_(None),
        )
        .first()
    )
    if not owned:
        raise HTTPException(status_code=404, detail="Trainer pokemon not found")
    return owned


def _create_owned_pokemon(
    db: Session, trainer: User, pokemon: Pokemon, is_starter: bool
) -> TrainerPokemon:
    level = 5 if is_starter else 1
    battle_stats = _calculate_battle_stats(pokemon.base_stats, level)
    known_moves = _known_moves_for_level(pokemon.moves or [], level)

    owned = TrainerPokemon(
        trainer_id=trainer.id,
        pokemon_id=pokemon.id,
        is_starter=is_starter,
        current_level=level,
        current_experience=0,
        current_hp=battle_stats["max_hp"],
        max_hp=battle_stats["max_hp"],
        attack=battle_stats["attack"],
        defense=battle_stats["defense"],
        sp_attack=battle_stats["sp_attack"],
        sp_defense=battle_stats["sp_defense"],
        speed=battle_stats["speed"],
        known_moves=known_moves,
        is_active=True,
    )
    db.add(owned)
    db.commit()
    db.refresh(owned)
    return owned


def select_starter_pokemon(
    db: Session, trainer: User, pokemon_name: str
) -> TrainerPokemon:
    normalized = pokemon_name.strip().lower()
    if normalized not in STARTER_NAMES:
        raise HTTPException(
            status_code=400, detail="Starter must be Bulbasaur, Charmander or Squirtle"
        )

    if trainer.starter_pokemon_selected:
        raise HTTPException(status_code=400, detail="Starter already selected")

    pokemon = get_or_create_pokemon(db, normalized)
    owned = _create_owned_pokemon(db, trainer, pokemon, is_starter=True)
    trainer.starter_pokemon_selected = True
    db.commit()
    return owned


def acquire_pokemon(db: Session, trainer: User, pokeapi_id: int) -> TrainerPokemon:
    pokemon = get_or_create_pokemon(db, str(pokeapi_id))

    if pokemon.name in STARTER_NAMES:
        raise HTTPException(
            status_code=400,
            detail="Starter pokemon can only be selected in starter flow",
        )

    existing = (
        db.query(TrainerPokemon)
        .filter(
            TrainerPokemon.trainer_id == trainer.id,
            TrainerPokemon.pokemon_id == pokemon.id,
            TrainerPokemon.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Pokemon already acquired")

    return _create_owned_pokemon(db, trainer, pokemon, is_starter=False)


def gain_experience(
    db: Session, trainer: User, trainer_pokemon_id: int, amount: int
) -> TrainerPokemon:
    if amount <= 0:
        raise HTTPException(
            status_code=400, detail="Experience amount must be greater than 0"
        )

    owned = _get_owned_pokemon_or_404(db, trainer.id, trainer_pokemon_id)
    owned.current_experience += amount

    previous_level = owned.current_level
    next_level = _experience_to_level(owned.current_experience)
    owned.current_level = next_level

    if next_level > previous_level:
        stats = _calculate_battle_stats(owned.pokemon.base_stats or {}, next_level)
        hp_delta = stats["max_hp"] - owned.max_hp
        owned.max_hp = stats["max_hp"]
        owned.current_hp = max(1, owned.current_hp + hp_delta)
        owned.attack = stats["attack"]
        owned.defense = stats["defense"]
        owned.sp_attack = stats["sp_attack"]
        owned.sp_defense = stats["sp_defense"]
        owned.speed = stats["speed"]
        owned.known_moves = _known_moves_for_level(
            owned.pokemon.moves or [], next_level
        )

    owned.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(owned)
    return owned


def get_trainer_pokemon_stats(
    db: Session, trainer: User, trainer_pokemon_id: int
) -> TrainerPokemon:
    return _get_owned_pokemon_or_404(db, trainer.id, trainer_pokemon_id)


def get_trainer_pokemon_moves(
    db: Session, trainer: User, trainer_pokemon_id: int
) -> TrainerPokemon:
    return _get_owned_pokemon_or_404(db, trainer.id, trainer_pokemon_id)


def list_trainer_pokemon(db: Session, trainer: User) -> list[TrainerPokemon]:
    return (
        db.query(TrainerPokemon)
        .filter(
            TrainerPokemon.trainer_id == trainer.id,
            TrainerPokemon.deleted_at.is_(None),
        )
        .all()
    )
