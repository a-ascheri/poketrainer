from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.game_save import GameSave, TrainerPartySlot
from src.models.trainer_pokemon import TrainerPokemon
from src.schemas.game_save import GameSaveUpdate


def get_game_save(trainer_id: int, db: Session) -> GameSave | None:
    return db.query(GameSave).filter(GameSave.trainer_id == trainer_id).first()


def get_game_save_or_404(trainer_id: int, db: Session) -> GameSave:
    save = get_game_save(trainer_id, db)
    if not save:
        raise HTTPException(
            status_code=404, detail="No existe partida guardada para este entrenador"
        )
    return save


def create_game_save(trainer_id: int, db: Session) -> GameSave:
    existing = get_game_save(trainer_id, db)
    if existing:
        raise HTTPException(
            status_code=409, detail="Ya existe una partida para este entrenador"
        )

    # Verificar que el entrenador tiene starter seleccionado
    starter = (
        db.query(TrainerPokemon)
        .filter(
            TrainerPokemon.trainer_id == trainer_id,
            TrainerPokemon.is_starter.is_(True),
            TrainerPokemon.is_active.is_(True),
        )
        .first()
    )
    if not starter:
        raise HTTPException(
            status_code=400,
            detail="El entrenador debe seleccionar su starter antes de comenzar",
        )

    save = GameSave(trainer_id=trainer_id)
    db.add(save)
    db.flush()  # obtener save.id antes de agregar party slot

    # Poner el starter en el slot 0 de la party
    slot = TrainerPartySlot(
        game_save_id=save.id,
        trainer_pokemon_id=starter.id,
        slot_position=0,
    )
    db.add(slot)
    db.commit()
    db.refresh(save)
    return save


def update_game_save(trainer_id: int, payload: GameSaveUpdate, db: Session) -> GameSave:
    save = get_game_save_or_404(trainer_id, db)

    update_fields = payload.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(save, field, value)

    db.commit()
    db.refresh(save)
    return save


def set_party_slot(
    trainer_id: int, trainer_pokemon_id: int, slot_position: int, db: Session
) -> TrainerPartySlot:
    if not (0 <= slot_position <= 5):
        raise HTTPException(
            status_code=400, detail="slot_position debe estar entre 0 y 5"
        )

    save = get_game_save_or_404(trainer_id, db)

    # Verificar que el pokemon pertenece al entrenador
    tp = (
        db.query(TrainerPokemon)
        .filter(
            TrainerPokemon.id == trainer_pokemon_id,
            TrainerPokemon.trainer_id == trainer_id,
            TrainerPokemon.is_active.is_(True),
        )
        .first()
    )
    if not tp:
        raise HTTPException(
            status_code=404,
            detail="Pokémon no encontrado en la colección del entrenador",
        )

    # Liberar el slot si ya estaba ocupado
    existing_slot = (
        db.query(TrainerPartySlot)
        .filter(
            TrainerPartySlot.game_save_id == save.id,
            TrainerPartySlot.slot_position == slot_position,
        )
        .first()
    )
    if existing_slot:
        db.delete(existing_slot)
        db.flush()

    slot = TrainerPartySlot(
        game_save_id=save.id,
        trainer_pokemon_id=trainer_pokemon_id,
        slot_position=slot_position,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def remove_party_slot(trainer_id: int, slot_position: int, db: Session) -> None:
    save = get_game_save_or_404(trainer_id, db)

    slot = (
        db.query(TrainerPartySlot)
        .filter(
            TrainerPartySlot.game_save_id == save.id,
            TrainerPartySlot.slot_position == slot_position,
        )
        .first()
    )
    if not slot:
        raise HTTPException(status_code=404, detail="No hay pokémon en ese slot")

    # No permitir quitar el último pokémon de la party
    total_slots = (
        db.query(TrainerPartySlot)
        .filter(TrainerPartySlot.game_save_id == save.id)
        .count()
    )
    if total_slots <= 1:
        raise HTTPException(
            status_code=400,
            detail="El entrenador debe tener al menos 1 pokémon en la party",
        )

    db.delete(slot)
    db.commit()
