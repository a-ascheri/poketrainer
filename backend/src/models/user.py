from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.database import Base


# Aquí se puede agregar más campos, como fecha de registro, etc.
# Relación con otros modelos (por ejemplo, pokemones del usuario)
# pokemons = relationship("Pokemon", back_populates="owner")
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(20), nullable=False, default="trainer", index=True)
    permissions = Column(JSON, nullable=False, default=list)
    force_password_change = Column(Boolean, nullable=False, default=False)
    starter_pokemon_selected = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trainer_pokemons = relationship("TrainerPokemon", back_populates="trainer")
