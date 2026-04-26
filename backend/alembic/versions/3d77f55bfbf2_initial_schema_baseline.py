"""initial_schema_baseline

Revision ID: 3d77f55bfbf2
Revises: 
Create Date: 2026-04-01 13:02:52.855519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d77f55bfbf2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Baseline: schema already applied via db_dump.sql
    # This migration exists only to establish the Alembic version history.
    # All 31 tables were created manually on 2026-04-01.
    pass


def downgrade() -> None:
    pass
