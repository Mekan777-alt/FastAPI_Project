"""add photo path to object profile

Revision ID: f465452de644
Revises: 4b4bb294ea65
Create Date: 2024-05-09 16:02:08.394043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f465452de644'
down_revision: Union[str, None] = '4b4bb294ea65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('object_profiles', sa.Column('photo_path', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('object_profiles', 'photo_path')
    # ### end Alembic commands ###
