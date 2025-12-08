"""add notifications table

Revision ID: 20251208_173708
Revises: 
Create Date: 2025-12-08 17:37:08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251208_173708'
down_revision = None  # Update this to the latest migration ID if there are existing migrations
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_role', sa.String(length=50), nullable=True),
        sa.Column('staff_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.Enum(
            'APPOINTMENT_CREATED',
            'APPOINTMENT_UPDATED',
            'APPOINTMENT_CANCELLED',
            'APPOINTMENT_RESCHEDULED',
            'APPOINTMENT_UPCOMING',
            'CLINIC_HOURS_UPDATED',
            'SYSTEM',
            name='notificationtype'
        ), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index('ix_notifications_user_role', 'notifications', ['user_role'], unique=False)
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'], unique=False)
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'], unique=False)
    op.create_index('ix_notifications_type', 'notifications', ['type'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_user_role', table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    
    # Drop table
    op.drop_table('notifications')
    
    # Drop enum type
    op.execute('DROP TYPE notificationtype')
