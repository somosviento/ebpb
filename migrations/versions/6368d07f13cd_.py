"""empty message

Revision ID: 6368d07f13cd
Revises: add_participant_fields, add_purpose_field
Create Date: 2025-05-15 13:54:17.289651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6368d07f13cd'
down_revision = ('add_participant_fields', 'add_purpose_field')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
