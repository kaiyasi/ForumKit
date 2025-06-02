"""create ig templates table

Revision ID: create_ig_templates_table
Revises: create_global_review_logs_table
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_ig_templates_table'
down_revision = 'create_global_review_logs_table'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'ig_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('background_image', sa.String(), nullable=False),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ig_templates_id'), 'ig_templates', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_ig_templates_id'), table_name='ig_templates')
    op.drop_table('ig_templates') 