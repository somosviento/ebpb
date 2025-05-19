"""añadir campos is_overnight y purpose a reservation_dates

Revision ID: add_reservation_date_fields
Revises: 
Create Date: 2025-05-15 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_reservation_date_fields'
down_revision = None  # Ajustar según corresponda
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columna is_overnight a la tabla reservation_dates
    op.add_column('reservation_dates', sa.Column('is_overnight', sa.Boolean(), nullable=True))
    op.execute('UPDATE reservation_dates SET is_overnight = 0')
    op.alter_column('reservation_dates', 'is_overnight', nullable=False, server_default=sa.text('0'))
    
    # Agregar columna purpose a la tabla reservation_dates
    op.add_column('reservation_dates', sa.Column('purpose', sa.String(50), nullable=True))


def downgrade():
    # Eliminar columna purpose de la tabla reservation_dates
    op.drop_column('reservation_dates', 'purpose')
    
    # Eliminar columna is_overnight de la tabla reservation_dates
    op.drop_column('reservation_dates', 'is_overnight')
