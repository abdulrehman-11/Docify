"""add google_calendar_event_id to appointments

Revision ID: 003
Revises: 002
Create Date: 2025-11-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add google_calendar_event_id column to appointments table"""
    op.add_column(
        'appointments',
        sa.Column('google_calendar_event_id', sa.String(255), nullable=True)
    )
    
    # Create index for faster lookups
    op.create_index(
        'ix_appointments_google_calendar_event_id',
        'appointments',
        ['google_calendar_event_id']
    )


def downgrade() -> None:
    """Remove google_calendar_event_id column"""
    op.drop_index('ix_appointments_google_calendar_event_id', table_name='appointments')
    op.drop_column('appointments', 'google_calendar_event_id')