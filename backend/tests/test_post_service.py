import pytest
from fastapi import HTTPException

from app.services import post as post_service_module
from app.schemas.post import PostCreate, PostRead

class DummyDB:
    pass

class DummyPost:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

@pytest.fixture
def mock_crud(monkeypatch):
    def create_with_author(db, obj_in, author_id=None):
        return DummyPost(id=1, title=obj_in.title, content=obj_in.content, is_anonymous=obj_in.is_anonymous, author_id=author_id, school_id=obj_in.school_id)
    monkeypatch.setattr(post_service_module.post_crud.post, "create_with_author", create_with_author)


def test_create_post_success(mock_crud):
    db = DummyDB()
    post_in = PostCreate(title="T", content="Hello", school_id=1, is_anonymous=True)
    result = post_service_module.create_post(db, post_in=post_in)
    assert isinstance(result, PostRead)
    assert result.title == "T"


def test_create_post_empty_content(mock_crud):
    db = DummyDB()
    post_in = PostCreate(title="T", content=" ", school_id=1, is_anonymous=True)
    with pytest.raises(HTTPException):
        post_service_module.create_post(db, post_in=post_in)


def test_create_post_requires_auth(mock_crud):
    db = DummyDB()
    post_in = PostCreate(title="T", content="Hi", school_id=1, is_anonymous=False)
    with pytest.raises(HTTPException):
        post_service_module.create_post(db, post_in=post_in, current_user=None)
