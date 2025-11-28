"""Add contact fields and denormalized date/day/time to appointments

Revision ID: 002
Revises: 001
Create Date: 2025-11-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("appointments", sa.Column("name", sa.String(length=255), nullable=True))
    op.add_column("appointments", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("appointments", sa.Column("phone", sa.String(length=20), nullable=True))
    op.add_column("appointments", sa.Column("date", sa.Date(), nullable=True))
    op.add_column("appointments", sa.Column("day", sa.String(length=16), nullable=True))
    op.add_column("appointments", sa.Column("time", sa.Time(timezone=True), nullable=True))

    # Backfill new columns using existing patient + appointment data
    op.execute(
        """
        UPDATE appointments AS a
        SET
            name = p.name,
            email = p.email,
            phone = p.phone,
            date = (a.start_time AT TIME ZONE 'UTC')::date,
            day = TO_CHAR(a.start_time AT TIME ZONE 'UTC', 'FMDay'),
            time = (a.start_time AT TIME ZONE 'UTC')::time
        FROM patients AS p
        WHERE a.patient_id = p.id
        """
    )

    op.alter_column("appointments", "name", existing_type=sa.String(length=255), nullable=False)
    op.alter_column("appointments", "email", existing_type=sa.String(length=255), nullable=False)
    op.alter_column("appointments", "phone", existing_type=sa.String(length=20), nullable=False)
    op.alter_column("appointments", "date", existing_type=sa.Date(), nullable=False)
    op.alter_column("appointments", "day", existing_type=sa.String(length=16), nullable=False)
    op.alter_column("appointments", "time", existing_type=sa.Time(timezone=True), nullable=False)

    op.create_index("ix_appointments_email", "appointments", ["email"])
    op.create_index("ix_appointments_phone", "appointments", ["phone"])
    op.create_index("ix_appointments_date", "appointments", ["date"])


def downgrade() -> None:
    op.drop_index("ix_appointments_date", table_name="appointments")
    op.drop_index("ix_appointments_phone", table_name="appointments")
    op.drop_index("ix_appointments_email", table_name="appointments")
    op.drop_column("appointments", "time")
    op.drop_column("appointments", "day")
    op.drop_column("appointments", "date")
    op.drop_column("appointments", "phone")
    op.drop_column("appointments", "email")
    op.drop_column("appointments", "name")


