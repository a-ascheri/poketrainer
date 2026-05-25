"""add roles soft delete and pokemon tables

Revision ID: b7f9c1e4a2f0
Revises: a12570f9730d
Create Date: 2026-05-24 13:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7f9c1e4a2f0"
down_revision: Union[str, None] = "a12570f9730d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("permissions", sa.JSON(), nullable=True))
    op.add_column(
        "users", sa.Column("force_password_change", sa.Boolean(), nullable=True)
    )
    op.add_column(
        "users", sa.Column("starter_pokemon_selected", sa.Boolean(), nullable=True)
    )
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.add_column(
        "users", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
    )
    op.add_column(
        "users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)
    )

    op.execute("UPDATE users SET role = 'trainer' WHERE role IS NULL")
    op.execute("UPDATE users SET permissions = '[]'::json WHERE permissions IS NULL")
    op.execute(
        "UPDATE users SET force_password_change = false WHERE force_password_change IS NULL"
    )
    op.execute(
        "UPDATE users SET starter_pokemon_selected = false WHERE starter_pokemon_selected IS NULL"
    )
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")

    op.alter_column("users", "role", nullable=False)
    op.alter_column("users", "permissions", nullable=False)
    op.alter_column("users", "force_password_change", nullable=False)
    op.alter_column("users", "starter_pokemon_selected", nullable=False)
    op.alter_column("users", "is_active", nullable=False)

    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)

    op.create_table(
        "pokemons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pokeapi_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("types", sa.JSON(), nullable=False),
        sa.Column("abilities", sa.JSON(), nullable=False),
        sa.Column("base_stats", sa.JSON(), nullable=False),
        sa.Column("moves", sa.JSON(), nullable=False),
        sa.Column("evolution_chain", sa.JSON(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pokemons_id"), "pokemons", ["id"], unique=False)
    op.create_index(op.f("ix_pokemons_name"), "pokemons", ["name"], unique=True)
    op.create_index(
        op.f("ix_pokemons_pokeapi_id"), "pokemons", ["pokeapi_id"], unique=True
    )

    op.create_table(
        "trainer_pokemon",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trainer_id", sa.Integer(), nullable=False),
        sa.Column("pokemon_id", sa.Integer(), nullable=False),
        sa.Column("is_starter", sa.Boolean(), nullable=False),
        sa.Column("current_level", sa.Integer(), nullable=False),
        sa.Column("current_experience", sa.Integer(), nullable=False),
        sa.Column("current_hp", sa.Integer(), nullable=False),
        sa.Column("max_hp", sa.Integer(), nullable=False),
        sa.Column("attack", sa.Integer(), nullable=False),
        sa.Column("defense", sa.Integer(), nullable=False),
        sa.Column("sp_attack", sa.Integer(), nullable=False),
        sa.Column("sp_defense", sa.Integer(), nullable=False),
        sa.Column("speed", sa.Integer(), nullable=False),
        sa.Column("known_moves", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["pokemon_id"], ["pokemons.id"]),
        sa.ForeignKeyConstraint(["trainer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_trainer_pokemon_id"), "trainer_pokemon", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_trainer_pokemon_is_active"),
        "trainer_pokemon",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_trainer_pokemon_pokemon_id"),
        "trainer_pokemon",
        ["pokemon_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_trainer_pokemon_trainer_id"),
        "trainer_pokemon",
        ["trainer_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_trainer_pokemon_trainer_id"), table_name="trainer_pokemon")
    op.drop_index(op.f("ix_trainer_pokemon_pokemon_id"), table_name="trainer_pokemon")
    op.drop_index(op.f("ix_trainer_pokemon_is_active"), table_name="trainer_pokemon")
    op.drop_index(op.f("ix_trainer_pokemon_id"), table_name="trainer_pokemon")
    op.drop_table("trainer_pokemon")

    op.drop_index(op.f("ix_pokemons_pokeapi_id"), table_name="pokemons")
    op.drop_index(op.f("ix_pokemons_name"), table_name="pokemons")
    op.drop_index(op.f("ix_pokemons_id"), table_name="pokemons")
    op.drop_table("pokemons")

    op.drop_index(op.f("ix_users_is_active"), table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")

    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "deleted_at")
    op.drop_column("users", "is_active")
    op.drop_column("users", "starter_pokemon_selected")
    op.drop_column("users", "force_password_change")
    op.drop_column("users", "permissions")
    op.drop_column("users", "role")
