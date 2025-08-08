from typing import Optional
from app.crud.school_d1 import school_d1
from app.schemas.school import SchoolCreate

# 信箱域名到學校代碼的映射
EMAIL_DOMAIN_TO_SCHOOL = {
    "test.edu.tw": "TEST",  # 測試學校
    "ntnu.edu.tw": "NTNU",  # 台師大
    "ntu.edu.tw": "NTU",    # 台大
    "nctu.edu.tw": "NCTU",  # 交大
}

def is_valid_edu_email(email: str) -> bool:
    """
    檢查是否為有效的教育信箱
    """
    return email.lower().endswith('edu.tw')

async def get_school_id_by_email_d1(email: str) -> Optional[int]:
    """
    根據郵件域名獲取學校 ID（D1 版本）
    """
    if not is_valid_edu_email(email):
        return None
        
    # 從郵件中提取學校域名
    domain = email.split('@')[1].lower()
    
    # 根據域名查找學校
    school = await school_d1.get_by_domain(domain)
    if not school:
        # 如果學校不存在，創建新學校
        school_name = EMAIL_DOMAIN_TO_SCHOOL.get(domain, domain.split('.')[0].upper())
        school_create = SchoolCreate(
            name=f"{school_name} 大學",
            domain=domain
        )
        school = await school_d1.create(school_create)
    
    return school["id"]

# 為了向後相容性保留原函數（但已淘汰）
def get_school_id_by_email(db, email: str) -> Optional[int]:
    """
    已淘汰：請使用 get_school_id_by_email_d1
    """
    # 這個函數已被淘汰，但保留以防某些地方還在使用
    return None 