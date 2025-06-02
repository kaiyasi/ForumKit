"""update school feature toggles table

Revision ID: update_school_feature_toggles
Revises: create_admin_logs_table
Create Date: 2024-03-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_school_feature_toggles'
down_revision = 'create_admin_logs_table'
branch_labels = None
depends_on = None

def upgrade():
    # 添加新欄位
    op.add_column('school_feature_toggles', sa.Column('enable_comments', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('school_feature_toggles', sa.Column('enable_cross_school', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('school_feature_toggles', sa.Column('ig_template_id', sa.Integer(), nullable=True))
    op.add_column('school_feature_toggles', sa.Column('ig_publish_auto', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('school_feature_toggles', sa.Column('discord_webhook_url', sa.String(), nullable=True))
    op.add_column('school_feature_toggles', sa.Column('discord_channel_name', sa.String(), nullable=True))
    op.add_column('school_feature_toggles', sa.Column('discord_report_webhook_url', sa.String(), nullable=True))
    op.add_column('school_feature_toggles', sa.Column('settings', sa.JSON(), nullable=True))

    # 添加外鍵約束
    op.create_foreign_key(
        'fk_school_feature_toggles_ig_template_id',
        'school_feature_toggles',
        'ig_templates',
        ['ig_template_id'],
        ['id'],
        ondelete='SET NULL'
    )

def downgrade():
    # 移除外鍵約束
    op.drop_constraint('fk_school_feature_toggles_ig_template_id', 'school_feature_toggles', type_='foreignkey')

    # 移除欄位
    op.drop_column('school_feature_toggles', 'settings')
    op.drop_column('school_feature_toggles', 'discord_report_webhook_url')
    op.drop_column('school_feature_toggles', 'discord_channel_name')
    op.drop_column('school_feature_toggles', 'discord_webhook_url')
    op.drop_column('school_feature_toggles', 'ig_publish_auto')
    op.drop_column('school_feature_toggles', 'ig_template_id')
    op.drop_column('school_feature_toggles', 'enable_cross_school')
    op.drop_column('school_feature_toggles', 'enable_comments') 