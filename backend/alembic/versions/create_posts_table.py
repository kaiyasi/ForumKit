"""create posts table

Revision ID: create_posts_table
Revises: initial_migration
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_posts_table'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # 創建 post_status 枚舉類型
    post_status = postgresql.ENUM('pending', 'approved', 'rejected', 'deleted', name='poststatus')
    post_status.create(op.get_bind())
    
    # 創建 posts 表
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('school_id', sa.Integer(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', 'deleted', name='poststatus'), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sensitive_reason', sa.String(length=200), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_comment', sa.String(length=500), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comment_count', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 創建索引
    op.create_index(op.f('ix_posts_title'), 'posts', ['title'], unique=False)
    op.create_index(op.f('ix_posts_status'), 'posts', ['status'], unique=False)
    op.create_index(op.f('ix_posts_created_at'), 'posts', ['created_at'], unique=False)

def downgrade():
    # 刪除索引
    op.drop_index(op.f('ix_posts_created_at'), table_name='posts')
    op.drop_index(op.f('ix_posts_status'), table_name='posts')
    op.drop_index(op.f('ix_posts_title'), table_name='posts')
    
    # 刪除表
    op.drop_table('posts')
    
    # 刪除枚舉類型
    post_status = postgresql.ENUM(name='poststatus')
    post_status.drop(op.get_bind()) 