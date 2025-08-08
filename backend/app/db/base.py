# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.school import School  # noqa
from app.models.post import Post  # noqa
from app.models.comment import Comment  # noqa
from app.models.review_log import ReviewLog  # noqa
from app.models.discussion_tag import DiscussionTag  # noqa
from app.models.internal_discussion import InternalDiscussion  # noqa
from app.models.global_discussion import GlobalDiscussion  # noqa
