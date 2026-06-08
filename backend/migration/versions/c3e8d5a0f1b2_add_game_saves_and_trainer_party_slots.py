"""add game_saves and trainer_party_slots tables

Revision ID: c3e8d5a0f1b2
Revises: b7f9c1e4a2f0
Create Date: 2026-05-31 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3e8d5a0f1b2"
down_revision: Union[str, None] = "b7f9c1e4a2f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "game_saves",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "trainer_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column(
            "map_id",
            sa.String(length=100),
            nullable=False,
            server_default="pallet_town",
        ),
        sa.Column("tile_x", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("tile_y", sa.Integer(), nullable=False, server_default="7"),
        sa.Column(
            "direction", sa.String(length=10), nullable=False, server_default="down"
        ),
        sa.Column("money", sa.Integer(), nullable=False, server_default="3000"),
        sa.Column(
            "play_time_seconds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("badges", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("inventory", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("game_flags", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "trainer_party_slots",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "game_save_id",
            sa.Integer(),
            sa.ForeignKey("game_saves.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "trainer_pokemon_id",
            sa.Integer(),
            sa.ForeignKey("trainer_pokemon.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("slot_position", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("trainer_party_slots")
    op.drop_table("game_saves")
