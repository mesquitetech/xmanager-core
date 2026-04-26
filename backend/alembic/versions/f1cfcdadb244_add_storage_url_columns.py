"""add_storage_url_columns

Revision ID: f1cfcdadb244
Revises: 3d77f55bfbf2
Create Date: 2026-04-01 17:06:08.392716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1cfcdadb244'
down_revision: Union[str, Sequence[str], None] = '3d77f55bfbf2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # seguros: agregar columnas de URL para Storage, hacer nullable las de contenido binario
    op.add_column("seguros", sa.Column("poliza_url", sa.String(500), nullable=True))
    op.add_column("seguros", sa.Column("contrato_url", sa.String(500), nullable=True))
    op.alter_column("seguros", "poliza_content", nullable=True)
    op.alter_column("seguros", "contrato_content", nullable=True)

    # expense_evidences: reemplazar esquema legacy por uno consistente con el router
    op.add_column("expense_evidences", sa.Column("file_name", sa.String(), nullable=True))
    op.add_column("expense_evidences", sa.Column("file_url", sa.String(500), nullable=True))
    op.add_column("expense_evidences", sa.Column("file_data", sa.Text(), nullable=True))
    op.add_column("expense_evidences", sa.Column("uploaded_by_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))

    # payment_evidences: agregar file_url, hacer nullable file_data
    op.add_column("payment_evidences", sa.Column("file_url", sa.String(500), nullable=True))
    op.alter_column("payment_evidences", "file_data", nullable=True)


def downgrade() -> None:
    op.drop_column("seguros", "poliza_url")
    op.drop_column("seguros", "contrato_url")

    op.drop_column("expense_evidences", "file_name")
    op.drop_column("expense_evidences", "file_url")
    op.drop_column("expense_evidences", "file_data")
    op.drop_column("expense_evidences", "uploaded_by_id")

    op.drop_column("payment_evidences", "file_url")
    op.alter_column("payment_evidences", "file_data", nullable=False)
