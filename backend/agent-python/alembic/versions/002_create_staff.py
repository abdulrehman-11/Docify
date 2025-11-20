"""create staff table

Revision ID: 002
Revises: 001
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create staff table"""
    op.create_table(
        'staff',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='staff'),
        sa.Column('permissions', JSON, nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_staff_id', 'staff', ['id'])
    op.create_index('ix_staff_email', 'staff', ['email'], unique=True)


def downgrade() -> None:
    """Drop staff table"""
    op.drop_index('ix_staff_email', table_name='staff')
    op.drop_index('ix_staff_id', table_name='staff')
    op.drop_table('staff')
