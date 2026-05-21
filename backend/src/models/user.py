from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
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
