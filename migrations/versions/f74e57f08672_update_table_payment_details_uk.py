"""update table payment details uk

Revision ID: f74e57f08672
Revises: 78d23071df20
Create Date: 2024-03-25 08:58:08.555896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f74e57f08672'
down_revision: Union[str, None] = '78d23071df20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_details_uk',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipient_name', sa.String(), nullable=False),
    sa.Column('account', sa.String(), nullable=False),
    sa.Column('contact_number', sa.String(), nullable=False),
    sa.Column('purpose_of_payment', sa.String(), nullable=False),
    sa.Column('bic', sa.String(), nullable=False),
    sa.Column('correspondent_account', sa.String(), nullable=False),
    sa.Column('bank_name', sa.String(), nullable=False),
    sa.Column('inn', sa.String(), nullable=False),
    sa.Column('kpp', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('payment_details')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment_details',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('bank_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('account_number', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('uk_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['uk_id'], ['uk_profiles.id'], name='payment_details_uk_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='payment_details_pkey')
    )
    op.drop_table('payment_details_uk')
    # ### end Alembic commands ###
