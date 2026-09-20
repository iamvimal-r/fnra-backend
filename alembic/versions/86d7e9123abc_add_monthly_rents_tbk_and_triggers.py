"""add_monthly_rents_tbk_and_triggers

Revision ID: 86d7e9123abc
Revises: 75c7fa376a2e
Create Date: 2026-09-20 09:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86d7e9123abc'
down_revision: Union[str, None] = '75c7fa376a2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create monthly_rents_tbk audit table
    op.create_table(
        'monthly_rents_tbk',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('rent_id', sa.Integer(), nullable=True),
        sa.Column('house_id', sa.String(length=255), nullable=True),
        sa.Column('house_number', sa.String(length=50), nullable=True),
        sa.Column('month', sa.String(length=50), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('operation', sa.String(length=20), nullable=False),
        sa.Column('posted_by', sa.String(length=255), server_default='system', nullable=True),
        sa.Column('posted_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_monthly_rents_tbk_id', 'monthly_rents_tbk', ['id'], unique=False)

    # 2. Create Triggers on monthly_rents
    op.execute("DROP TRIGGER IF EXISTS trg_monthly_rents_after_insert;")
    op.execute("""
        CREATE TRIGGER trg_monthly_rents_after_insert
        AFTER INSERT ON monthly_rents
        FOR EACH ROW
        BEGIN
            INSERT INTO monthly_rents_tbk (rent_id, house_id, house_number, month, year, amount, status, payment_date, operation, posted_by, posted_date)
            VALUES (NEW.id, NEW.house_id, NEW.house_number, NEW.month, NEW.year, NEW.amount, NEW.status, NEW.payment_date, 'INSERT', 'system', NOW());
        END;
    """)

    op.execute("DROP TRIGGER IF EXISTS trg_monthly_rents_after_update;")
    op.execute("""
        CREATE TRIGGER trg_monthly_rents_after_update
        AFTER UPDATE ON monthly_rents
        FOR EACH ROW
        BEGIN
            INSERT INTO monthly_rents_tbk (rent_id, house_id, house_number, month, year, amount, status, payment_date, operation, posted_by, posted_date)
            VALUES (NEW.id, NEW.house_id, NEW.house_number, NEW.month, NEW.year, NEW.amount, NEW.status, NEW.payment_date, 'UPDATE', 'system', NOW());
        END;
    """)

    op.execute("DROP TRIGGER IF EXISTS trg_monthly_rents_after_delete;")
    op.execute("""
        CREATE TRIGGER trg_monthly_rents_after_delete
        AFTER DELETE ON monthly_rents
        FOR EACH ROW
        BEGIN
            INSERT INTO monthly_rents_tbk (rent_id, house_id, house_number, month, year, amount, status, payment_date, operation, posted_by, posted_date)
            VALUES (OLD.id, OLD.house_id, OLD.house_number, OLD.month, OLD.year, OLD.amount, OLD.status, OLD.payment_date, 'DELETE', 'system', NOW());
        END;
    """)


def downgrade() -> None:
    # 1. Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_monthly_rents_after_insert;")
    op.execute("DROP TRIGGER IF EXISTS trg_monthly_rents_after_update;")
    op.execute("DROP TRIGGER IF EXISTS trg_monthly_rents_after_delete;")

    # 2. Drop table
    op.drop_index('ix_monthly_rents_tbk_id', table_name='monthly_rents_tbk')
    op.drop_table('monthly_rents_tbk')
