"""Add clinic breaks and holidays

Revision ID: 004
Revises: 003
Create Date: 2025-11-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add break time columns to clinic_hours
    op.add_column('clinic_hours', sa.Column('break_start', sa.Time(), nullable=True))
    op.add_column('clinic_hours', sa.Column('break_end', sa.Time(), nullable=True))
    op.add_column('clinic_hours', sa.Column('updated_at', sa.DateTime(timezone=True), 
                                            server_default=sa.func.now(), nullable=False))
    
    # Create clinic_holidays table for specific date holidays
    op.create_table(
        'clinic_holidays',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_full_day', sa.Boolean(), default=True, nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', name='uq_clinic_holidays_date')
    )


def downgrade() -> None:
    # Drop clinic_holidays table
    op.drop_table('clinic_holidays')
    
    # Remove columns from clinic_hours
    op.drop_column('clinic_hours', 'updated_at')
    op.drop_column('clinic_hours', 'break_end')
    op.drop_column('clinic_hours', 'break_start')
