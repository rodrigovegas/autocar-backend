"""ampliar_url_imagen_video_cloudinary

Revision ID: 0ade6a75143c
Revises: d4e5f6a7b8c9
Create Date: 2026-05-29 02:37:01.779233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ade6a75143c'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'contenido_educativo', 'url_imagen',
        existing_type=sa.String(500),
        type_=sa.String(1000),
        existing_nullable=True
    )
    op.alter_column(
        'contenido_educativo', 'url_video',
        existing_type=sa.String(500),
        type_=sa.String(1000),
        existing_nullable=True
    )
    op.add_column(
        'contenido_educativo',
        sa.Column('cloudinary_public_id', sa.String(500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('contenido_educativo', 'cloudinary_public_id')
    op.alter_column(
        'contenido_educativo', 'url_video',
        existing_type=sa.String(1000),
        type_=sa.String(500),
        existing_nullable=True
    )
    op.alter_column(
        'contenido_educativo', 'url_imagen',
        existing_type=sa.String(1000),
        type_=sa.String(500),
        existing_nullable=True
    )