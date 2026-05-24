from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.database import Base


class Pokemon(Base):
    __tablename__ = "pokemons"

    id = Column(Integer, primary_key=True, index=True)
    pokeapi_id = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String(80), nullable=False, unique=True, index=True)
    types = Column(JSON, nullable=False, default=list)
    abilities = Column(JSON, nullable=False, default=list)
    base_stats = Column(JSON, nullable=False, default=dict)
    moves = Column(JSON, nullable=False, default=list)
    evolution_chain = Column(JSON, nullable=True)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trainer_pokemons = relationship("TrainerPokemon", back_populates="pokemon")
