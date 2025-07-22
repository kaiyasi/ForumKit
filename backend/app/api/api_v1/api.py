from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    users,
    posts,
    comments,
    reviews,
    school,
    global_,
    dev,
    admin
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(school.router, prefix="/school", tags=["school"])
api_router.include_router(global_.router, prefix="/global", tags=["global"])
api_router.include_router(dev.router, prefix="/dev", tags=["dev"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"]) 
