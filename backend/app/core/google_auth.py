from typing import Optional, Tuple
import hashlib
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings

def verify_google_token(token: str) -> Optional[dict]:
    """
    驗證 Google ID token
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return None
            
        return idinfo
    except ValueError:
        return None

def is_valid_edu_email(email: str) -> bool:
    """
    檢查是否為有效的教育信箱
    """
    return email.endswith('@xxhs.edu.tw')

def get_email_hash(email: str) -> str:
    """
    產生信箱雜湊值
    """
    return hashlib.sha256(email.lower().encode()).hexdigest()

def extract_user_info(idinfo: dict) -> Tuple[str, str, str]:
    """
    從 Google ID token 資訊中提取用戶資料
    """
    email = idinfo['email']
    name = idinfo.get('name', email.split('@')[0])
    email_hash = get_email_hash(email)
    
    return email, name, email_hash 