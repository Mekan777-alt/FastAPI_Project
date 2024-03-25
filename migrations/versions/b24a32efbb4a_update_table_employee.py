"""update table employee

Revision ID: b24a32efbb4a
Revises: b9778e769d53
Create Date: 2024-03-04 00:37:07.850280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b24a32efbb4a'
down_revision: Union[str, None] = 'b9778e769d53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('uk_employees',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(), nullable=True),
    sa.Column('uk_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['uk_id'], ['uk_profiles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    op.drop_table('employees')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employees',
    sa.Column('uuid', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('uk_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['uk_id'], ['uk_profiles.id'], name='employees_uk_id_fkey'),
    sa.PrimaryKeyConstraint('uuid', name='employees_pkey')
    )
    op.drop_table('uk_employees')
    # ### end Alembic commands ###