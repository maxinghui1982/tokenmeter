"""
TokenMeter Auth Routes
用户认证 API
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import jwt
import os

from ..database.models import get_db
from ..database.user_models import User, UserManager
from ..utils.logging_config import get_logger, info, error

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
logger = get_logger(__name__)

# JWT 配置
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

security = HTTPBearer()


# ============ Pydantic 模型 ============


class UserRegister(BaseModel):
    """用户注册请求"""

    username: str = Field(..., min_length=3, max_length=64)
    email: str = Field(..., max_length=256)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""

    username: str  # 可以是用户名或邮箱
    password: str


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_admin: bool
    created_at: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token 响应"""

    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


# ============ JWT 工具函数 ============


def create_access_token(user_id: int) -> str:
    """创建 JWT Token"""
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {"user_id": user_id, "exp": expiration, "iat": datetime.utcnow()}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入用）"""
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    manager = UserManager(db)
    user = manager.get_user_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or disabled")

    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """获取当前管理员用户"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ============ API 路由 ============


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        manager = UserManager(db)
        user = manager.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )

        token = create_access_token(user.id)

        info(logger, "User registered", user_id=user.id, username=user.username)

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION_HOURS * 3600,
            "user": user.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error(logger, "Registration failed", error=str(e))
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    try:
        manager = UserManager(db)
        user = manager.authenticate(credentials.username, credentials.password)

        token = create_access_token(user.id)

        info(logger, "User logged in", user_id=user.id, username=user.username)

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION_HOURS * 3600,
            "user": user.to_dict(),
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        error(logger, "Login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Login failed")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user.to_dict()


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    if not current_user.check_password(old_password):
        raise HTTPException(status_code=400, detail="Invalid old password")

    current_user.set_password(new_password)
    db.commit()

    info(logger, "Password changed", user_id=current_user.id)

    return {"success": True, "message": "Password changed successfully"}
