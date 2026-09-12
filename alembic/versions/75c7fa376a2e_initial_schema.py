"""initial_schema

Revision ID: 75c7fa376a2e
Revises: None
Create Date: 2026-09-12 16:35:38.290038

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75c7fa376a2e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='resident'),
        sa.Column('profile_image', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. notices
    op.create_table(
        'notices',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('date_posted', sa.DateTime(), nullable=True),
        sa.Column('author_id', sa.String(length=255), nullable=True),
    )
    op.create_index('ix_notices_id', 'notices', ['id'], unique=False)

    # 3. complaints
    op.create_table(
        'complaints',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Pending'),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('date_submitted', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_complaints_id', 'complaints', ['id'], unique=False)

    # 4. bills
    op.create_table(
        'bills',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Unpaid'),
    )
    op.create_index('ix_bills_id', 'bills', ['id'], unique=False)

    # 5. houses
    op.create_table(
        'houses',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('house_number', sa.String(length=50), nullable=False),
        sa.Column('block', sa.String(length=50), nullable=False),
        sa.Column('owner_name', sa.String(length=255), nullable=False),
        sa.Column('family_members', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('last_payment_date', sa.DateTime(), nullable=True),
        sa.Column('last_payment_month', sa.String(length=100), server_default='No payments yet'),
    )
    op.create_index('ix_houses_id', 'houses', ['id'], unique=False)
    op.create_index('ix_houses_house_number', 'houses', ['house_number'], unique=True)

    # 6. visitors
    op.create_table(
        'visitors',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('house_number', sa.String(length=50), nullable=False),
        sa.Column('purpose', sa.String(length=255), nullable=True),
        sa.Column('entry_time', sa.DateTime(), nullable=True),
        sa.Column('exit_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Entered'),
    )
    op.create_index('ix_visitors_id', 'visitors', ['id'], unique=False)

    # 7. staff
    op.create_table(
        'staff',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('shift', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
    )
    op.create_index('ix_staff_id', 'staff', ['id'], unique=False)

    # 8. monthly_rents
    op.create_table(
        'monthly_rents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('house_id', sa.String(length=255), nullable=True),
        sa.Column('house_number', sa.String(length=50), nullable=True),
        sa.Column('month', sa.String(length=50), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Paid'),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_monthly_rents_id', 'monthly_rents', ['id'], unique=False)

    # 9. moms
    op.create_table(
        'moms',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('meeting_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_moms_id', 'moms', ['id'], unique=False)

    # 10. amenities
    op.create_table(
        'amenities',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('is_available', sa.Boolean(), server_default=sa.text('1')),
    )
    op.create_index('ix_amenities_id', 'amenities', ['id'], unique=False)

    # 11. expenses
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('expense_date', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=255), server_default='system'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_expenses_id', 'expenses', ['id'], unique=False)

    # 12. incomes
    op.create_table(
        'incomes',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('income_date', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=255), server_default='system'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_incomes_id', 'incomes', ['id'], unique=False)

    # 13. committee_members
    op.create_table(
        'committee_members',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('designation', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), server_default='99'),
        sa.Column('published', sa.Boolean(), server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_committee_members_id', 'committee_members', ['id'], unique=False)

    # 14. cms_pages
    op.create_table(
        'cms_pages',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_cms_pages_id', 'cms_pages', ['id'], unique=False)
    op.create_index('ix_cms_pages_slug', 'cms_pages', ['slug'], unique=True)

    # 15. contacts
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
    )
    op.create_index('ix_contacts_id', 'contacts', ['id'], unique=False)

    # 16. slides
    op.create_table(
        'slides',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('subtitle', sa.String(length=255), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('order', sa.Integer(), server_default='0'),
        sa.Column('active', sa.Boolean(), server_default=sa.text('1')),
    )
    op.create_index('ix_slides_id', 'slides', ['id'], unique=False)

    # 17. news
    op.create_table(
        'news',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), server_default='general'),
        sa.Column('published', sa.Boolean(), server_default=sa.text('1')),
        sa.Column('date', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_news_id', 'news', ['id'], unique=False)

    # 18. gallery
    op.create_table(
        'gallery',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=50), server_default='general'),
        sa.Column('order', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_gallery_id', 'gallery', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('gallery')
    op.drop_table('news')
    op.drop_table('slides')
    op.drop_table('contacts')
    op.drop_table('cms_pages')
    op.drop_table('committee_members')
    op.drop_table('incomes')
    op.drop_table('expenses')
    op.drop_table('amenities')
    op.drop_table('moms')
    op.drop_table('monthly_rents')
    op.drop_table('staff')
    op.drop_table('visitors')
    op.drop_table('houses')
    op.drop_table('bills')
    op.drop_table('complaints')
    op.drop_table('notices')
    op.drop_table('users')
