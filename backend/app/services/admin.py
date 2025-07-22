from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud import admin_log as admin_log_crud
from app.crud import post as post_crud
from app.crud import user as user_crud
from app.crud import school as school_crud
from app.schemas.admin_log import AdminLogCreate, AdminLogQuery
from app.models.user import User, UserRole

class AdminService:
    async def get_dashboard_stats(
        self,
        db: Session,
        *,
        user: User
    ) -> Dict[str, Any]:
        """
        獲取儀表板統計資料
        """
        # 檢查權限
        if user.role not in [UserRole.ADMIN, UserRole.REVIEWER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員或審核員權限"
            )

        stats = {
            "total_posts": 0,
            "pending_posts": 0,
            "total_users": 0,
            "total_schools": 0,
            "recent_activities": []
        }

        # 如果是審核員，只顯示本校資料
        if user.role == UserRole.REVIEWER:
            stats["total_posts"] = post_crud.post.count_by_school(
                db=db,
                school_id=user.school_id
            )
            stats["pending_posts"] = post_crud.post.count_by_school_and_status(
                db=db,
                school_id=user.school_id,
                status="pending"
            )
        else:
            # 管理員可以看到所有資料
            stats["total_posts"] = post_crud.post.count(db=db)
            stats["pending_posts"] = post_crud.post.count_by_status(
                db=db,
                status="pending"
            )
            stats["total_users"] = user_crud.user.count(db=db)
            stats["total_schools"] = school_crud.school.count(db=db)

        # 獲取最近的管理日誌
        stats["recent_activities"] = admin_log_crud.admin_log.get_recent(
            db=db,
            limit=10
        )

        return stats

    async def log_admin_action(
        self,
        db: Session,
        *,
        admin: User,
        action: str,
        target_type: str,
        target_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        記錄管理員操作
        """
        log_in = AdminLogCreate(
            admin_id=admin.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address
        )
        admin_log_crud.admin_log.create(db=db, obj_in=log_in)

    async def get_admin_logs(
        self,
        db: Session,
        *,
        query: AdminLogQuery,
        user: User
    ) -> List[Dict[str, Any]]:
        """
        獲取管理日誌
        """
        # 檢查權限
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理員權限"
            )

        return admin_log_crud.admin_log.get_multi(
            db=db,
            skip=query.skip,
            limit=query.limit,
            action=query.action,
            target_type=query.target_type,
            admin_id=query.admin_id,
            start_date=query.start_date,
            end_date=query.end_date
        )

admin_service = AdminService() 
