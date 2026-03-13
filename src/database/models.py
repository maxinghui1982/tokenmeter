"""
TokenMeter Database Models
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    Text, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

Base = declarative_base()


class UsageRecord(Base):
    """AI API 使用记录"""
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 请求标识
    request_id = Column(String(64), unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 提供商和模型
    provider = Column(String(32), index=True)  # openai, azure, claude, etc.
    model = Column(String(64), index=True)     # gpt-4, gpt-3.5-turbo, etc.
    
    # Token 用量
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # 成本（按美元计算）
    cost_input = Column(Float, default=0.0)    # 输入成本
    cost_output = Column(Float, default=0.0)   # 输出成本
    cost_total = Column(Float, default=0.0)    # 总成本
    
    # 业务归因标签
    project = Column(String(128), index=True)  # 项目名称
    team = Column(String(64), index=True)      # 团队
    environment = Column(String(32), index=True)  # 环境: dev, staging, prod
    user_id = Column(String(64), index=True)   # 用户ID
    
    # 请求详情（可选）
    request_path = Column(String(256))         # API 路径
    status_code = Column(Integer)              # HTTP 状态码
    latency_ms = Column(Integer)               # 请求延迟（毫秒）
    
    # 索引优化查询
    __table_args__ = (
        Index('idx_project_timestamp', 'project', 'timestamp'),
        Index('idx_team_timestamp', 'team', 'timestamp'),
        Index('idx_provider_model', 'provider', 'model'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'provider': self.provider,
            'model': self.model,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'cost_input': round(self.cost_input, 6),
            'cost_output': round(self.cost_output, 6),
            'cost_total': round(self.cost_total, 6),
            'project': self.project,
            'team': self.team,
            'environment': self.environment,
            'user_id': self.user_id,
            'request_path': self.request_path,
            'status_code': self.status_code,
            'latency_ms': self.latency_ms,
        }


class Budget(Base):
    """预算配置"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True)
    scope_type = Column(String(32))  # global, project, team, user
    scope_value = Column(String(128))  # 具体的项目名/团队名等
    
    budget_amount = Column(Float)  # 预算金额（美元）
    period = Column(String(32), default='monthly')  # daily, weekly, monthly
    alert_thresholds = Column(String(256))  # JSON: [50, 80, 100]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProviderConfig(Base):
    """MaaS 提供商配置"""
    __tablename__ = "provider_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), unique=True)  # openai, azure, claude
    base_url = Column(String(256))
    api_key_encrypted = Column(Text)  # 加密存储
    is_active = Column(Integer, default=1)
    
    # 定价配置（JSON格式，按模型）
    pricing_config = Column(Text)


# 数据库连接管理
class DatabaseManager:
    def __init__(self, db_path: str = "./data/tokenmeter.db"):
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        
    def init_database(self):
        """初始化数据库"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={"check_same_thread": False},
            echo=False
        )
        
        # 创建表
        Base.metadata.create_all(bind=self.engine)
        
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )
        
        print(f"✅ Database initialized at {self.db_path}")
        
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()


# 全局实例
db_manager = DatabaseManager()


def get_db():
    """FastAPI 依赖注入用"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()