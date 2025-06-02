"""update user and school models

Revision ID: update_user_and_school_models
Revises: add_google_auth_fields
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_user_and_school_models'
down_revision = 'add_google_auth_fields'
branch_labels = None
depends_on = None

def upgrade():
    # 創建 UserRole 枚舉類型
    user_role = postgresql.ENUM('user', 'reviewer', 'admin', 'dev', name='userrole')
    user_role.create(op.get_bind())

    # 更新 users 表
    op.alter_column('users', 'role',
               existing_type=sa.String(),
               type_=sa.Enum('user', 'reviewer', 'admin', 'dev', name='userrole'),
               existing_nullable=False)

    # 更新 schools 表
    op.add_column('schools', sa.Column('slug', sa.String(), nullable=True))
    op.add_column('schools', sa.Column('ig_enabled', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('schools', sa.Column('dc_enabled', sa.Boolean(), server_default='false', nullable=False))
    
    # 更新現有記錄
    op.execute("""
        UPDATE schools 
        SET slug = LOWER(REPLACE(name, ' ', '-'))
        WHERE slug IS NULL
    """)
    
    # 設置非空約束
    op.alter_column('schools', 'slug',
               existing_type=sa.String(),
               nullable=False)
    
    # 創建索引
    op.create_index(op.f('ix_schools_slug'), 'schools', ['slug'], unique=True)

def downgrade():
    # 刪除索引
    op.drop_index(op.f('ix_schools_slug'), table_name='schools')
    
    # 刪除欄位
    op.drop_column('schools', 'dc_enabled')
    op.drop_column('schools', 'ig_enabled')
    op.drop_column('schools', 'slug')
    
    # 恢復 role 欄位
    op.alter_column('users', 'role',
               existing_type=sa.Enum('user', 'reviewer', 'admin', 'dev', name='userrole'),
               type_=sa.String(),
               existing_nullable=False)
    
    # 刪除 UserRole 枚舉類型
    user_role = postgresql.ENUM('user', 'reviewer', 'admin', 'dev', name='userrole')
    user_role.drop(op.get_bind()) 