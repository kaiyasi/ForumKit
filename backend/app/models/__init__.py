from .user import User
from .school import School
from .post import Post
from .comment import Comment
from .discussion_tag import DiscussionTag, DiscussionTagAssociation
from .internal_discussion import InternalDiscussion
from .global_discussion import GlobalDiscussion, GlobalDiscussionPostAssociation

# 導出所有模型
__all__ = [
    "User",
    "School",
    "Post",
    "Comment",
    "DiscussionTag",
    "InternalDiscussion",
    "GlobalDiscussion",
]
