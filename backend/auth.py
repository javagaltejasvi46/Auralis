"""
Authentication and authorization utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import Therapist, get_db

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # Change in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"❌ JWT decode error: {e}")
        raise JWTError(f"Invalid token: {e}")

async def get_current_therapist(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Therapist:
    """Get current authenticated therapist"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print(f"🔍 Verifying token: {token[:20]}...")
        payload = verify_token(token)
        print(f"✅ Token payload: {payload}")
        therapist_id_str: str = payload.get("sub")
        if therapist_id_str is None:
            print("❌ No therapist ID in token")
            raise credentials_exception
        therapist_id: int = int(therapist_id_str)
        print(f"👤 Therapist ID from token: {therapist_id}")
    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise credentials_exception
    
    therapist = db.query(Therapist).filter(Therapist.id == therapist_id).first()
    if therapist is None:
        print(f"❌ No therapist found with ID: {therapist_id}")
        raise credentials_exception
    
    print(f"✅ Therapist authenticated: {therapist.username}")
    
    if not therapist.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account"
        )
    
    return therapist

async def get_current_active_therapist(
    current_therapist: Therapist = Depends(get_current_therapist)
) -> Therapist:
    """Get current active and verified therapist"""
    if not current_therapist.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please contact administrator."
        )
    return current_therapist
