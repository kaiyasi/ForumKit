import asyncio
import pytest
from fastapi import HTTPException

from app.dependencies.auth import require_role

class DummyUser:
    def __init__(self, role):
        self.role = role
        self.is_active = True


def test_require_role_success():
    checker = require_role("admin")
    user = DummyUser("admin")
    assert asyncio.run(checker(current_user=user)) == user


def test_require_role_failure():
    checker = require_role("admin")
    user = DummyUser("user")
    with pytest.raises(HTTPException):
        asyncio.run(checker(current_user=user))
