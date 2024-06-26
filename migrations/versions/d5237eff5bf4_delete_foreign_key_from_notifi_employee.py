"""delete foreign key from notifi employee

Revision ID: d5237eff5bf4
Revises: fd9666bd2d39
Create Date: 2024-05-21 16:25:14.339814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5237eff5bf4'
down_revision: Union[str, None] = 'fd9666bd2d39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('employee_notification_object_id_fkey', 'employee_notification', type_='foreignkey')
    op.create_foreign_key(None, 'employee_notification', 'object_profiles', ['object_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'employee_notification', type_='foreignkey')
    op.create_foreign_key('employee_notification_object_id_fkey', 'employee_notification', 'uk_employees', ['object_id'], ['id'])
    # ### end Alembic commands ###
