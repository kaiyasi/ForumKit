import sys
import types
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import asyncio
from datetime import datetime

# create stub aiohttp module
aiohttp = types.ModuleType('aiohttp')
class DummyResponse:
    def __init__(self, status=204):
        self.status = status
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
class DummySession:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    def post(self, url, json):
        return DummyResponse()
aiohttp.ClientSession = lambda *args, **kwargs: DummySession()
sys.modules['aiohttp'] = aiohttp


# stub sqlalchemy.orm.Session
sqlalchemy = types.ModuleType('sqlalchemy')
orm = types.ModuleType('sqlalchemy.orm')
class Session:  # simple placeholder
    pass
orm.Session = Session
sqlalchemy.orm = orm
sys.modules['sqlalchemy'] = sqlalchemy
sys.modules['sqlalchemy.orm'] = orm

# stub config settings
config = types.ModuleType('app.core.config')
config.settings = types.SimpleNamespace(FRONTEND_URL='http://frontend')
sys.modules['app.core.config'] = config

# stub CRUD modules
post_obj = types.SimpleNamespace(
    id=1,
    title='Test',
    content='content',
    created_at=datetime.now(),
    school_id=1
)
post_module = types.ModuleType('app.crud.post')
post_module.post = types.SimpleNamespace(get=lambda db, id: post_obj)
sys.modules['app.crud.post'] = post_module

discord_entity = types.SimpleNamespace(
    post_webhook_url='http://webhook',
    report_webhook_url='http://report',
    FRONTEND_URL='http://frontend'
)
crud_ds_module = types.ModuleType('app.crud.discord_settings')
crud_ds_module.discord_settings = types.SimpleNamespace(
    get_by_school=lambda db, school_id: discord_entity,
    get=lambda db, id: discord_entity,
    create=lambda *a, **k: discord_entity,
    update=lambda *a, **k: discord_entity,
)
sys.modules['app.crud.discord_settings'] = crud_ds_module

# stub schema module
schema_module = types.ModuleType('app.schemas.discord_settings')
schema_module.DiscordSettingsCreate = type('DiscordSettingsCreate', (), {})
schema_module.DiscordSettingsUpdate = type('DiscordSettingsUpdate', (), {})
sys.modules['app.schemas.discord_settings'] = schema_module

# stub user model
model_user = types.ModuleType('app.models.user')
class UserRole:
    ADMIN = 'admin'
class User:
    def __init__(self, role):
        self.role = role
        self.username = 'tester'
model_user.UserRole = UserRole
model_user.User = User
sys.modules['app.models.user'] = model_user

# import the service after stubs are ready
from app.services.discord import discord_service


def test_publish_post_success():
    admin = model_user.User(UserRole.ADMIN)
    result = asyncio.run(discord_service.publish_post(db=None, post_id=1, admin=admin))
    assert result == {'success': True}
