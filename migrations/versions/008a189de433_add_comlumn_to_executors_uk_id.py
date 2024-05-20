"""add comlumn to executors uk_id

Revision ID: 008a189de433
Revises: c083a962579e
Create Date: 2024-05-18 15:18:49.242004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008a189de433'
down_revision: Union[str, None] = 'c083a962579e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('executor_profiles', sa.Column('uk_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'executor_profiles', 'uk_profiles', ['uk_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'executor_profiles', type_='foreignkey')
    op.drop_column('executor_profiles', 'uk_id')
    # ### end Alembic commands ###