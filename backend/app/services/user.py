from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserUpdate, RoleAssignment, UserQuery
from app.models.user import User, UserRole

class UserService:
    async def assign_role(
        self,
        db: Session,
        *,
        role_assignment: RoleAssignment,
        admin: User
    ) -> dict:
        """
        指派用戶角色
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        # 檢查目標用戶是否存在
        user = user_crud.user.get_by_email(db, email=role_assignment.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用戶不存在"
            )

        # 檢查用戶是否已綁定學校
        if not user.school_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用戶尚未綁定學校"
            )

        # 檢查角色是否有效
        if role_assignment.role not in [UserRole.REVIEWER, UserRole.DESIGNER, UserRole.SYNC]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的角色類型"
            )

        # 更新用戶角色
        user = user_crud.user.update(
            db=db,
            db_obj=user,
            obj_in={"role": role_assignment.role}
        )

        return user

    async def get_users(
        self,
        db: Session,
        *,
        query: UserQuery,
        admin: User
    ) -> List[dict]:
        """
        獲取用戶列表
        """
        # 檢查權限
        if admin.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        return user_crud.user.get_multi(
            db=db,
            skip=query.skip,
            limit=query.limit,
            school_id=query.school_id,
            role=query.role,
            search=query.search
        )

user_service = UserService() 
