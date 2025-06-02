"""create global discussion tables

Revision ID: create_global_discussion_tables
Revises: create_internal_discussion_tables
Create Date: 2024-03-21 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_global_discussion_tables'
down_revision = 'create_internal_discussion_tables'
branch_labels = None
depends_on = None

def upgrade():
    # 創建跨校討論表
    op.create_table(
        'global_discussions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['global_discussions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_global_discussions_id'),
        'global_discussions',
        ['id'],
        unique=False
    )
    op.create_index(
        op.f('ix_global_discussions_author_id'),
        'global_discussions',
        ['author_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_global_discussions_parent_id'),
        'global_discussions',
        ['parent_id'],
        unique=False
    )

    # 創建討論-貼文關聯表
    op.create_table(
        'global_discussion_post_associations',
        sa.Column('discussion_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['discussion_id'], ['global_discussions.id'], ),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.PrimaryKeyConstraint('discussion_id', 'post_id')
    )

def downgrade():
    # 刪除討論-貼文關聯表
    op.drop_table('global_discussion_post_associations')
    
    # 刪除跨校討論表
    op.drop_index(op.f('ix_global_discussions_parent_id'), table_name='global_discussions')
    op.drop_index(op.f('ix_global_discussions_author_id'), table_name='global_discussions')
    op.drop_index(op.f('ix_global_discussions_id'), table_name='global_discussions')
    op.drop_table('global_discussions') 