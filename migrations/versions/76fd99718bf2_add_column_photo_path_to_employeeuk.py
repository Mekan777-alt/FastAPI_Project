"""add column photo path to EmployeeUK

Revision ID: 76fd99718bf2
Revises: fba1f29e3775
Create Date: 2024-03-09 17:38:02.477711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76fd99718bf2'
down_revision: Union[str, None] = 'fba1f29e3775'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('uk_employees', sa.Column('photo_path', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('uk_employees', 'photo_path')
    # ### end Alembic commands ###
