"""create school feature toggles table

Revision ID: create_school_feature_toggles_table
Revises: create_discord_settings_table
Create Date: 2024-03-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_school_feature_toggles_table'
down_revision = 'create_discord_settings_table'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'school_feature_toggles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('school_id', sa.Integer(), nullable=False),
        sa.Column('enable_ig', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('enable_discord', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_school_feature_toggles_id'), 'school_feature_toggles', ['id'], unique=False)
    op.create_index(op.f('ix_school_feature_toggles_school_id'), 'school_feature_toggles', ['school_id'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_school_feature_toggles_school_id'), table_name='school_feature_toggles')
    op.drop_index(op.f('ix_school_feature_toggles_id'), table_name='school_feature_toggles')
    op.drop_table('school_feature_toggles') 