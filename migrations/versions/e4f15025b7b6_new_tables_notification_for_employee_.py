"""new tables notification for employee and uk

Revision ID: e4f15025b7b6
Revises: 057d349af814
Create Date: 2024-05-20 14:09:49.601123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4f15025b7b6'
down_revision: Union[str, None] = '057d349af814'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('uk_notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('icon_path', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('uk_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['uk_id'], ['uk_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('employee_notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('icon_path', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['uk_employees.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('employee_notification')
    op.drop_table('uk_notification')
    # ### end Alembic commands ###
