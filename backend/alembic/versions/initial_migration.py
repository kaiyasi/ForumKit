"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-03-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 創建學校表
    op.create_table(
        'schools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_schools_code'), 'schools', ['code'], unique=True)
    op.create_index(op.f('ix_schools_name'), 'schools', ['name'], unique=True)

    # 創建用戶表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('school_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 創建文章表
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('school_id', sa.Integer(), nullable=False),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_title'), 'posts', ['title'], unique=False)

    # 創建評論表
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('comments')
    op.drop_index(op.f('ix_posts_title'), table_name='posts')
    op.drop_table('posts')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_schools_name'), table_name='schools')
    op.drop_index(op.f('ix_schools_code'), table_name='schools')
    op.drop_table('schools') 