"""create ig accounts table

Revision ID: create_ig_accounts_table
Revises: create_ig_templates_table
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_ig_accounts_table'
down_revision = 'create_ig_templates_table'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'ig_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('school_id', sa.Integer(), nullable=False),
        sa.Column('ig_username', sa.String(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ig_accounts_id'), 'ig_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_ig_accounts_school_id'), 'ig_accounts', ['school_id'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_ig_accounts_school_id'), table_name='ig_accounts')
    op.drop_index(op.f('ix_ig_accounts_id'), table_name='ig_accounts')
    op.drop_table('ig_accounts') 