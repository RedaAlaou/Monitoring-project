"""
JWT Authentication Service for Device Management Microservice.
Handles JWT token validation and decoding.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from helpers.config import JWT_SECRET_KEY, JWT_ALGORITHM, logger


# HTTP Bearer token security scheme
security = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str  # Subject (user email/ID)
    role: Optional[bool] = None  # User role (admin or not)
    exp: Optional[datetime] = None  # Expiration time
    iat: Optional[datetime] = None  # Issued at time


class AuthUser(BaseModel):
    """Authenticated user model extracted from token."""
    email: str
    is_admin: bool = False


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenPayload if valid, None if invalid
    """
    try:
        payload: Dict[str, Any] = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM]
        )
        
        if payload:
            return TokenPayload(
                sub=payload.get('sub', ''),
                role=payload.get('role', False),
                exp=datetime.fromtimestamp(payload.get('exp', 0), tz=timezone.utc) if payload.get('exp') else None,
                iat=datetime.fromtimestamp(payload.get('iat', 0), tz=timezone.utc) if payload.get('iat') else None
            )
            
    except JWTError as e:
        logger.error(f"JWT decoding error: {e}")
        return None
    
    return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthUser:
    """
    FastAPI dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        AuthUser object with email and admin status
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    token_payload = decode_token(token)
    
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return AuthUser(
        email=token_payload.sub,
        is_admin=bool(token_payload.role)
    )


def verify_admin_user(
    current_user: AuthUser = Depends(get_current_user)
) -> AuthUser:
    """
    FastAPI dependency to verify the current user is an admin.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        AuthUser object if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    
    return current_user


def create_test_token(
    email: str, 
    is_admin: bool = False, 
    expires_delta: int = 30
) -> str:
    """
    Create a JWT token for testing purposes.
    
    Args:
        email: User email
        is_admin: Whether user is admin
        expires_delta: Token expiration in minutes
        
    Returns:
        JWT token string
    """
    from datetime import timedelta
    
    payload = {
        "sub": email,
        "role": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_delta),
        "iat": datetime.now(timezone.utc),
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
