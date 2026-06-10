from datetime import datetime

from pydantic import BaseModel, Field


class PartySlotRead(BaseModel):
    id: int
    slot_position: int
    trainer_pokemon_id: int

    class Config:
        from_attributes = True


class GameSaveUpdate(BaseModel):
    """Payload para actualizar la posición/estado de la partida (autosave / manual save)."""

    map_id: str | None = None
    tile_x: int | None = None
    tile_y: int | None = None
    direction: str | None = Field(None, pattern="^(up|down|left|right)$")
    money: int | None = Field(None, ge=0)
    play_time_seconds: int | None = Field(None, ge=0)
    badges: list[str] | None = None
    inventory: dict[str, int] | None = None
    game_flags: dict[str, bool | str | int] | None = None


class GameSaveRead(BaseModel):
    id: int
    trainer_id: int
    map_id: str
    tile_x: int
    tile_y: int
    direction: str
    money: int
    play_time_seconds: int
    badges: list[str]
    inventory: dict
    game_flags: dict
    party_slots: list[PartySlotRead]
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
