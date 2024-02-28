"""update table Documents

Revision ID: e894c4f78daf
Revises: 9a8e591701ab
Create Date: 2024-02-28 20:12:07.461347

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e894c4f78daf'
down_revision: Union[str, None] = '9a8e591701ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
