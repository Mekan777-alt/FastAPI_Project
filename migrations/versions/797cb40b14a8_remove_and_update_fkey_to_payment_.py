"""remove and update fkey to payment details

Revision ID: 797cb40b14a8
Revises: fd56d78d4f26
Create Date: 2024-03-25 09:04:41.513482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '797cb40b14a8'
down_revision: Union[str, None] = 'fd56d78d4f26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
