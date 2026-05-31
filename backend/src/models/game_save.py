from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.database import Base

DEFAULT_STARTING_MAP = "pallet_town"
DEFAULT_TILE_X = 5
DEFAULT_TILE_Y = 7
DEFAULT_DIRECTION = "down"


class GameSave(Base):
    """Estado completo de la partida de un entrenador."""

    __tablename__ = "game_saves"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Posición en el mundo
    map_id = Column(String(100), nullable=False, default=DEFAULT_STARTING_MAP)
    tile_x = Column(Integer, nullable=False, default=DEFAULT_TILE_X)
    tile_y = Column(Integer, nullable=False, default=DEFAULT_TILE_Y)
    direction = Column(String(10), nullable=False, default=DEFAULT_DIRECTION)

    # Recursos
    money = Column(Integer, nullable=False, default=3000)
    play_time_seconds = Column(Integer, nullable=False, default=0)

    # Progreso (JSON flexible para agregar flags sin migrar)
    badges = Column(JSON, nullable=False, default=list)       # ["boulder_badge", ...]
    inventory = Column(JSON, nullable=False, default=dict)    # {"poke_ball": 5, ...}
    game_flags = Column(JSON, nullable=False, default=dict)   # {"rival_first_battle": True, ...}

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trainer = relationship("User", back_populates="game_save")
    party_slots = relationship(
        "TrainerPartySlot", back_populates="game_save", cascade="all, delete-orphan"
    )


class TrainerPartySlot(Base):
    """Party activa del entrenador (máximo 6 pokémon en orden de slot)."""

    __tablename__ = "trainer_party_slots"

    id = Column(Integer, primary_key=True, index=True)
    game_save_id = Column(Integer, ForeignKey("game_saves.id"), nullable=False, index=True)
    trainer_pokemon_id = Column(
        Integer, ForeignKey("trainer_pokemon.id"), nullable=False, index=True
    )
    slot_position = Column(Integer, nullable=False)  # 0-5

    game_save = relationship("GameSave", back_populates="party_slots")
    trainer_pokemon = relationship("TrainerPokemon", back_populates="party_slots")
