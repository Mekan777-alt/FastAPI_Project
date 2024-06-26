"""added comlumn photo path to invoice

Revision ID: 4b4bb294ea65
Revises: 5a723c2eed49
Create Date: 2024-05-09 13:06:18.967327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b4bb294ea65'
down_revision: Union[str, None] = '5a723c2eed49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invoice_history', sa.Column('photo_path', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invoice_history', 'photo_path')
    # ### end Alembic commands ###
