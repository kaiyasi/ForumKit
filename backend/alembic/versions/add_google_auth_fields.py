"""add google auth fields

Revision ID: add_google_auth_fields
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_google_auth_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 添加新欄位
    op.add_column('users', sa.Column('email_hash', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('role', sa.String(), nullable=True, server_default='user'))
    
    # 更新現有記錄
    op.execute("""
        UPDATE users 
        SET email_hash = encode(digest(lower(email), 'sha256'), 'hex'),
            is_verified = true
        WHERE email_hash IS NULL
    """)
    
    # 設置非空約束
    op.alter_column('users', 'email_hash',
               existing_type=sa.String(),
               nullable=False)
    op.alter_column('users', 'is_verified',
               existing_type=sa.Boolean(),
               nullable=False)
    op.alter_column('users', 'role',
               existing_type=sa.String(),
               nullable=False)
    
    # 創建索引
    op.create_index(op.f('ix_users_email_hash'), 'users', ['email_hash'], unique=True)

def downgrade():
    # 刪除索引
    op.drop_index(op.f('ix_users_email_hash'), table_name='users')
    
    # 刪除欄位
    op.drop_column('users', 'role')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'email_hash') 