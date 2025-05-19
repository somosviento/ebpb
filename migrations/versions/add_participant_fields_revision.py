"""Add CUIL and birth_date to participants table

Revision ID: add_participant_fields
Revises: 5283adc0498e
Create Date: 2025-05-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_participant_fields'
down_revision = '5283adc0498e'
branch_labels = None
depends_on = None


def upgrade():
    # Add CUIL column
    op.add_column('participants', sa.Column('cuil', sa.String(20), nullable=True))
    # Add birth_date column
    op.add_column('participants', sa.Column('birth_date', sa.Date(), nullable=True))


def downgrade():
    # Remove columns if needed to rollback
    op.drop_column('participants', 'cuil')
    op.drop_column('participants', 'birth_date')
