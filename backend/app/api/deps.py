from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User

def get_db_session() -> Session:
    """
    Get database session dependency
    """
    return get_db()

def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user
    """
    return get_current_active_user(db)

def get_current_user_optional(db: Session = Depends(get_db)) -> Optional[User]:
    """
    Get current authenticated user (optional, allows anonymous access)
    """
    try:
        return get_current_active_user(db)
    except HTTPException:
        return None

def require_role(required_role: str):
    """
    Create a dependency that requires a specific user role
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        from app.models.user import UserRole
        
        # Convert string to UserRole enum
        try:
            role_enum = UserRole(required_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid role: {required_role}"
            )
        
        if current_user.role != role_enum:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker

def get_current_active_user_with_role(required_roles):
    """
    Create a dependency that requires specific user role(s)
    """
    from app.models.user import UserRole
    from typing import List, Union
    
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Handle both single role and list of roles
        if isinstance(required_roles, (list, tuple)):
            allowed_roles = required_roles
        else:
            allowed_roles = [required_roles]
        
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker
