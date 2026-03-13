"""
TokenMeter User Models
用户认证模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Session
import bcrypt

from ..database.models import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    
    # 用户信息
    full_name = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def set_password(self, password: str):
        """设置密码"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class UserManager:
    """用户管理器"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str = None, is_admin: bool = False) -> User:
        """创建用户"""
        # 检查用户名和邮箱是否已存在
        if self.db.query(User).filter(User.username == username).first():
            raise ValueError("Username already exists")
        
        if self.db.query(User).filter(User.email == email).first():
            raise ValueError("Email already exists")
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_admin=is_admin
        )
        user.set_password(password)
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate(self, username: str, password: str) -> User:
        """用户认证"""
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            raise ValueError("User not found")
        
        if not user.is_active:
            raise ValueError("User is disabled")
        
        if not user.check_password(password):
            raise ValueError("Invalid password")
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def get_user_by_id(self, user_id: int) -> User:
        """根据 ID 获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> User:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()