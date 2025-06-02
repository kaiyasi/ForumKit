"""create internal discussion tables

Revision ID: create_internal_discussion_tables
Revises: update_school_feature_toggles
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_internal_discussion_tables'
down_revision = 'update_school_feature_toggles'
branch_labels = None
depends_on = None

def upgrade():
    # 創建討論標籤表
    op.create_table(
        'discussion_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('color', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(
        op.f('ix_discussion_tags_id'),
        'discussion_tags',
        ['id'],
        unique=False
    )

    # 創建內部討論表
    op.create_table(
        'internal_discussions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('school_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['internal_discussions.id'], ),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_internal_discussions_id'),
        'internal_discussions',
        ['id'],
        unique=False
    )
    op.create_index(
        op.f('ix_internal_discussions_school_id'),
        'internal_discussions',
        ['school_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_internal_discussions_author_id'),
        'internal_discussions',
        ['author_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_internal_discussions_parent_id'),
        'internal_discussions',
        ['parent_id'],
        unique=False
    )

    # 創建討論-標籤關聯表
    op.create_table(
        'discussion_tag_associations',
        sa.Column('discussion_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['discussion_id'], ['internal_discussions.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['discussion_tags.id'], ),
        sa.PrimaryKeyConstraint('discussion_id', 'tag_id')
    )

def downgrade():
    # 刪除討論-標籤關聯表
    op.drop_table('discussion_tag_associations')
    
    # 刪除內部討論表
    op.drop_index(op.f('ix_internal_discussions_parent_id'), table_name='internal_discussions')
    op.drop_index(op.f('ix_internal_discussions_author_id'), table_name='internal_discussions')
    op.drop_index(op.f('ix_internal_discussions_school_id'), table_name='internal_discussions')
    op.drop_index(op.f('ix_internal_discussions_id'), table_name='internal_discussions')
    op.drop_table('internal_discussions')
    
    # 刪除討論標籤表
    op.drop_index(op.f('ix_discussion_tags_id'), table_name='discussion_tags')
    op.drop_table('discussion_tags') 