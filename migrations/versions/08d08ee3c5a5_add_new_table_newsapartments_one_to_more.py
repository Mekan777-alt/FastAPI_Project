"""add new table NewsApartments one-to-more

Revision ID: 08d08ee3c5a5
Revises: 25a10719b7b4
Create Date: 2024-05-15 22:51:41.021702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08d08ee3c5a5'
down_revision: Union[str, None] = '25a10719b7b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news_apartments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('apartment_id', sa.Integer(), nullable=True),
    sa.Column('news_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['apartment_id'], ['apartment_profiles.id'], ),
    sa.ForeignKeyConstraint(['news_id'], ['news.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('news_apartments')
    # ### end Alembic commands ###