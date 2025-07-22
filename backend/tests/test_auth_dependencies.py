import pytest
from fastapi import HTTPException

from app.dependencies.auth import check_permissions


class DummyUser:
    def __init__(self, role="user", is_superuser=False, is_active=True):
        self.role = role
        self.is_superuser = is_superuser
        self.is_active = is_active


def test_superuser_bypass():
    user = DummyUser(role="user", is_superuser=True)
    checker = check_permissions(["admin"])
    assert checker(current_user=user) is user


def test_permission_allowed():
    user = DummyUser(role="admin")
    checker = check_permissions(["admin", "reviewer"])
    assert checker(current_user=user) is user


def test_permission_denied():
    user = DummyUser(role="user")
    checker = check_permissions(["admin", "reviewer"])
    with pytest.raises(HTTPException):
        checker(current_user=user)
