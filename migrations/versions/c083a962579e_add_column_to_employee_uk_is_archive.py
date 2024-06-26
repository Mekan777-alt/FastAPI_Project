"""add column to employee uk is_archive

Revision ID: c083a962579e
Revises: 869ee1484940
Create Date: 2024-05-17 16:03:42.667012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c083a962579e'
down_revision: Union[str, None] = '869ee1484940'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('uk_employees', sa.Column('is_archive', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('uk_employees', 'is_archive')
    # ### end Alembic commands ###
