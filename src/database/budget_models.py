"""
TokenMeter Budget Models
预算管理数据模型
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import Session

from ..database.models import Base, db_manager


class BudgetPeriod(str, Enum):
    """预算周期"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BudgetScope(str, Enum):
    """预算范围类型"""
    GLOBAL = "global"
    PROJECT = "project"
    TEAM = "team"
    USER = "user"


class Budget(Base):
    """预算配置表"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    
    # 预算范围
    scope_type = Column(String(32), default=BudgetScope.GLOBAL.value)  # global/project/team/user
    scope_value = Column(String(128), nullable=True)  # 具体的项目名/团队名等
    
    # 预算金额（美元）
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="USD")
    
    # 预算周期
    period = Column(String(32), default=BudgetPeriod.MONTHLY.value)
    
    # 预警阈值（JSON格式：[50, 80, 100]）
    alert_thresholds = Column(Text, default="[50, 80, 100]")
    
    # 通知配置
    webhook_url = Column(String(512), nullable=True)  # 飞书/钉钉/Slack webhook
    email = Column(String(256), nullable=True)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "scope_type": self.scope_type,
            "scope_value": self.scope_value,
            "amount": self.amount,
            "currency": self.currency,
            "period": self.period,
            "alert_thresholds": json.loads(self.alert_thresholds) if self.alert_thresholds else [50, 80, 100],
            "webhook_url": self.webhook_url,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BudgetAlert(Base):
    """预算告警记录表"""
    __tablename__ = "budget_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    budget_id = Column(Integer, nullable=False)
    
    # 告警信息
    threshold_percent = Column(Integer, nullable=False)  # 触发的阈值百分比
    current_usage = Column(Float, nullable=False)  # 当前使用量
    current_percent = Column(Float, nullable=False)  # 当前使用百分比
    
    # 告警状态
    status = Column(String(32), default="sent")  # sent/acknowledged/resolved
    
    # 通知信息
    notification_sent = Column(Boolean, default=False)
    notification_error = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "budget_id": self.budget_id,
            "threshold_percent": self.threshold_percent,
            "current_usage": self.current_usage,
            "current_percent": self.current_percent,
            "status": self.status,
            "notification_sent": self.notification_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BudgetCalculator:
    """预算计算引擎"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def calculate_current_usage(self, budget: Budget) -> dict:
        """
        计算预算当前使用量
        
        Returns:
            {
                "total_cost": float,  # 总成本
                "total_requests": int,  # 总请求数
                "period_start": datetime,  # 周期开始时间
                "period_end": datetime,  # 周期结束时间
            }
        """
        from ..database.models import UsageRecord
        from sqlalchemy import func
        
        # 计算周期时间范围
        period_start, period_end = self._get_period_range(budget.period)
        
        # 构建查询
        query = self.db.query(
            func.sum(UsageRecord.cost_total).label("total_cost"),
            func.count(UsageRecord.id).label("total_requests")
        ).filter(
            UsageRecord.timestamp >= period_start,
            UsageRecord.timestamp < period_end
        )
        
        # 根据范围过滤
        if budget.scope_type == BudgetScope.PROJECT.value and budget.scope_value:
            query = query.filter(UsageRecord.project == budget.scope_value)
        elif budget.scope_type == BudgetScope.TEAM.value and budget.scope_value:
            query = query.filter(UsageRecord.team == budget.scope_value)
        elif budget.scope_type == BudgetScope.USER.value and budget.scope_value:
            query = query.filter(UsageRecord.user_id == budget.scope_value)
        
        result = query.first()
        
        return {
            "total_cost": result.total_cost or 0.0,
            "total_requests": result.total_requests or 0,
            "period_start": period_start,
            "period_end": period_end,
        }
    
    def _get_period_range(self, period: str) -> tuple:
        """获取周期时间范围"""
        now = datetime.utcnow()
        
        if period == BudgetPeriod.DAILY.value:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == BudgetPeriod.WEEKLY.value:
            # 本周一开始
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(weeks=1)
        elif period == BudgetPeriod.MONTHLY.value:
            # 本月一号
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        elif period == BudgetPeriod.QUARTERLY.value:
            # 本季度开始
            quarter = (now.month - 1) // 3
            start = now.replace(month=quarter * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            if quarter == 3:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=quarter * 3 + 4)
        elif period == BudgetPeriod.YEARLY.value:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=start.year + 1)
        else:
            # 默认月度
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(month=start.month + 1)
        
        return start, end
    
    def check_budget_thresholds(self, budget: Budget) -> list:
        """
        检查预算阈值
        
        Returns:
            触发的阈值列表
        """
        import json
        
        usage = self.calculate_current_usage(budget)
        current_cost = usage["total_cost"]
        
        if budget.amount <= 0:
            return []
        
        current_percent = (current_cost / budget.amount) * 100
        
        thresholds = json.loads(budget.alert_thresholds) if budget.alert_thresholds else [50, 80, 100]
        triggered = []
        
        for threshold in thresholds:
            if current_percent >= threshold:
                # 检查是否已经发送过该阈值的告警
                existing_alert = self.db.query(BudgetAlert).filter(
                    BudgetAlert.budget_id == budget.id,
                    BudgetAlert.threshold_percent == threshold
                ).first()
                
                if not existing_alert:
                    triggered.append({
                        "threshold": threshold,
                        "current_percent": current_percent,
                        "current_cost": current_cost,
                    })
        
        return triggered