"""create admin logs table

Revision ID: create_admin_logs_table
Revises: create_school_feature_toggles_table
Create Date: 2024-03-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_admin_logs_table'
down_revision = 'create_school_feature_toggles_table'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'admin_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_logs_id'), 'admin_logs', ['id'], unique=False)
    op.create_index(op.f('ix_admin_logs_admin_id'), 'admin_logs', ['admin_id'], unique=False)
    op.create_index(op.f('ix_admin_logs_action'), 'admin_logs', ['action'], unique=False)
    op.create_index(op.f('ix_admin_logs_target_type'), 'admin_logs', ['target_type'], unique=False)
    op.create_index(op.f('ix_admin_logs_created_at'), 'admin_logs', ['created_at'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_admin_logs_created_at'), table_name='admin_logs')
    op.drop_index(op.f('ix_admin_logs_target_type'), table_name='admin_logs')
    op.drop_index(op.f('ix_admin_logs_action'), table_name='admin_logs')
    op.drop_index(op.f('ix_admin_logs_admin_id'), table_name='admin_logs')
    op.drop_index(op.f('ix_admin_logs_id'), table_name='admin_logs')
    op.drop_table('admin_logs') 