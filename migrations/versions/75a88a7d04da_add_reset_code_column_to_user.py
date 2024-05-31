"""add reset_code column to user

Revision ID: 75a88a7d04da
Revises: 094fb2bf8872
Create Date: 2024-05-29 12:22:39.351200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75a88a7d04da'
down_revision: Union[str, None] = '094fb2bf8872'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tenant_profiles', sa.Column('reset_code', sa.String(), nullable=True))
    op.add_column('uk_employees', sa.Column('reset_code', sa.String(), nullable=True))
    op.add_column('uk_profiles', sa.Column('reset_code', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('uk_profiles', 'reset_code')
    op.drop_column('uk_employees', 'reset_code')
    op.drop_column('tenant_profiles', 'reset_code')
    # ### end Alembic commands ###