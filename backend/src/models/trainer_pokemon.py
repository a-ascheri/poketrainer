from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.database import Base


class TrainerPokemon(Base):
    __tablename__ = "trainer_pokemon"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pokemon_id = Column(Integer, ForeignKey("pokemons.id"), nullable=False, index=True)
    is_starter = Column(Boolean, nullable=False, default=False)
    current_level = Column(Integer, nullable=False, default=1)
    current_experience = Column(Integer, nullable=False, default=0)
    current_hp = Column(Integer, nullable=False, default=10)
    max_hp = Column(Integer, nullable=False, default=10)
    attack = Column(Integer, nullable=False, default=1)
    defense = Column(Integer, nullable=False, default=1)
    sp_attack = Column(Integer, nullable=False, default=1)
    sp_defense = Column(Integer, nullable=False, default=1)
    speed = Column(Integer, nullable=False, default=1)
    known_moves = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trainer = relationship("User", back_populates="trainer_pokemons")
    pokemon = relationship("Pokemon", back_populates="trainer_pokemons")
