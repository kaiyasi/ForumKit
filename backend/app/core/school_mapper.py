from typing import Optional
from sqlalchemy.orm import Session
from app.crud import school as school_crud

# 信箱域名到學校代碼的映射
EMAIL_DOMAIN_TO_SCHOOL = {
    "xxhs.edu.tw": "XXHS",  # 示例：新興高中
    "yyhs.edu.tw": "YYHS",  # 示例：陽明高中
    "zzhs.edu.tw": "ZZHS",  # 示例：中正高中
}

def is_valid_edu_email(email: str) -> bool:
    """
    檢查是否為有效的教育信箱
    """
    return email.lower().endswith('edu.tw')

def get_school_id_by_email(db: Session, email: str) -> Optional[int]:
    """
    根據郵件域名獲取學校 ID
    """
    if not is_valid_edu_email(email):
        return None
        
    # 從郵件中提取學校域名
    domain = email.split('@')[1].lower()
    school_code = domain.split('.')[0].upper()  # 例如：xxhs.edu.tw -> XXHS
    
    # 獲取或創建學校
    school = school_crud.get_by_code(db, code=school_code)
    if not school:
        # 如果學校不存在，創建新學校
        school = school_crud.create(db, obj_in={
            "code": school_code,
            "name": f"{school_code} 高中",
            "slug": school_code.lower(),
            "ig_enabled": True,
            "dc_enabled": True
        })
    
    return school.id 