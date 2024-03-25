"""drop tables performer_profiles and invoice_history yes

Revision ID: d32afdeabcf0
Revises: 2673d5324201
Create Date: 2024-03-24 12:01:46.573738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd32afdeabcf0'
down_revision: Union[str, None] = '2673d5324201'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invoice_history')
    op.drop_table('performer_profiles')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('performer_profiles',
    sa.Column('uuid', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('contact_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('specialization', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('bank_details', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('uuid', name='performer_profiles_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('invoice_history',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('issue_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('payment_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('notification_sent', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('performer_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('object_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['object_id'], ['object_profiles.id'], name='invoice_history_object_id_fkey'),
    sa.ForeignKeyConstraint(['performer_id'], ['performer_profiles.uuid'], name='invoice_history_performer_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='invoice_history_pkey')
    )
    # ### end Alembic commands ###