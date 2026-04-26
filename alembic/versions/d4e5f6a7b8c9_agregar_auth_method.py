"""agregar_auth_method

Revision ID: d4e5f6a7b8c9
Revises: c866f81ea343
Create Date: 2026-04-26 00:00:00.000000

Agrega la columna auth_method a las tablas usuario y taller para registrar
el método de autenticación con que se creó cada cuenta ('email' o 'google').
Los registros existentes reciben 'email' como valor por defecto.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c866f81ea343"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Columna auth_method en usuario — registros existentes quedan como 'email'
    op.add_column(
        "usuario",
        sa.Column(
            "auth_method",
            sa.String(20),
            nullable=False,
            server_default="email",
        ),
    )
    op.create_check_constraint(
        "ck_usuario_auth_method",
        "usuario",
        "auth_method IN ('email', 'google')",
    )

    # Columna auth_method en taller — registros existentes quedan como 'email'
    op.add_column(
        "taller",
        sa.Column(
            "auth_method",
            sa.String(20),
            nullable=False,
            server_default="email",
        ),
    )
    op.create_check_constraint(
        "ck_taller_auth_method",
        "taller",
        "auth_method IN ('email', 'google')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_taller_auth_method", "taller", type_="check")
    op.drop_column("taller", "auth_method")

    op.drop_constraint("ck_usuario_auth_method", "usuario", type_="check")
    op.drop_column("usuario", "auth_method")
