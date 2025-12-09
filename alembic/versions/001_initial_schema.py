"""Initial schema with seed data

Revision ID: 001
Revises:
Create Date: 2025-11-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum type
    appointment_status = ENUM('CONFIRMED', 'CANCELLED', 'RESCHEDULED', 'COMPLETED', name='appointmentstatus', create_type=True)

    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('insurance_provider', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_patients_email', 'patients', ['email'])

    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', appointment_status, nullable=False, server_default='CONFIRMED'),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_appointments_patient_id', 'appointments', ['patient_id'])
    op.create_index('idx_appointments_start_time', 'appointments', ['start_time'])
    op.create_index('idx_appointments_status', 'appointments', ['status'])
    op.create_index('idx_appointments_start_status', 'appointments', ['start_time', 'status'])

    # Create clinic_hours table
    op.create_table(
        'clinic_hours',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('day_of_week >= 0 AND day_of_week <= 6', name='valid_day_of_week'),
        sa.PrimaryKeyConstraint('id')
    )

    # Seed clinic hours: Monday-Friday 9 AM - 5 PM
    op.execute("""
        INSERT INTO clinic_hours (day_of_week, start_time, end_time) VALUES
        (0, '09:00:00', '17:00:00'),  -- Monday
        (1, '09:00:00', '17:00:00'),  -- Tuesday
        (2, '09:00:00', '17:00:00'),  -- Wednesday
        (3, '09:00:00', '17:00:00'),  -- Thursday
        (4, '09:00:00', '17:00:00');  -- Friday
    """)

def downgrade() -> None:
    op.drop_table('clinic_hours')
    op.drop_index('idx_appointments_start_status', 'appointments')
    op.drop_index('idx_appointments_status', 'appointments')
    op.drop_index('idx_appointments_start_time', 'appointments')
    op.drop_index('idx_appointments_patient_id', 'appointments')
    op.drop_table('appointments')
    op.drop_index('idx_patients_email', 'patients')
    op.drop_table('patients')
    ENUM(name='appointmentstatus').drop(op.get_bind(), checkfirst=True)
