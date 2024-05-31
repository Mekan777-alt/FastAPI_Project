"""add foreign key for contacts

Revision ID: 4c075d0dc5d5
Revises: 9e5fa34b86b8
Create Date: 2024-05-30 15:31:05.327396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c075d0dc5d5'
down_revision: Union[str, None] = '9e5fa34b86b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('uk_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'contacts', 'uk_profiles', ['uk_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contacts', type_='foreignkey')
    op.drop_column('contacts', 'uk_id')
    # ### end Alembic commands ###