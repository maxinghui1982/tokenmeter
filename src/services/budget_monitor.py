"""
TokenMeter Budget Monitor
预算监控任务
"""
import asyncio
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from ..database.models import db_manager
from ..database.budget_models import Budget, BudgetAlert, BudgetCalculator
from ..services.notification import NotificationManager
from ..utils.logging_config import get_logger, info, error

logger = get_logger(__name__)


class BudgetMonitor:
    """预算监控器"""
    
    def __init__(self):
        self.notification_manager = NotificationManager()
        self.running = False
    
    async def start_monitoring(self, interval_seconds: int = 300):
        """
        启动预算监控循环
        
        Args:
            interval_seconds: 检查间隔（默认 5 分钟）
        """
        self.running = True
        info(logger, "Budget monitor started", interval_seconds=interval_seconds)
        
        while self.running:
            try:
                await self.check_all_budgets()
            except Exception as e:
                error(logger, "Budget check failed", error=str(e))
            
            await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        info(logger, "Budget monitor stopped")
    
    async def check_all_budgets(self):
        """检查所有活跃预算"""
        db = db_manager.get_session()
        
        try:
            # 获取所有活跃预算
            budgets = db.query(Budget).filter(Budget.is_active == True).all()
            
            info(logger, "Checking budgets", count=len(budgets))
            
            for budget in budgets:
                await self._check_single_budget(db, budget)
                
        finally:
            db.close()
    
    async def _check_single_budget(self, db: Session, budget: Budget):
        """检查单个预算"""
        calculator = BudgetCalculator(db)
        
        try:
            # 检查阈值
            triggered = calculator.check_budget_thresholds(budget)
            
            if triggered:
                usage = calculator.calculate_current_usage(budget)
                
                for trigger in triggered:
                    # 创建告警记录
                    alert = BudgetAlert(
                        budget_id=budget.id,
                        threshold_percent=trigger["threshold"],
                        current_usage=trigger["current_cost"],
                        current_percent=trigger["current_percent"]
                    )
                    
                    db.add(alert)
                    db.commit()
                    
                    info(logger, "Budget threshold triggered",
                         budget_id=budget.id,
                         threshold=trigger["threshold"],
                         percent=trigger["current_percent"])
                    
                    # 发送通知
                    if budget.webhook_url:
                        await self._send_notification(budget, trigger)
                        
        except Exception as e:
            error(logger, "Failed to check budget",
                  budget_id=budget.id,
                  error=str(e))
    
    async def _send_notification(self, budget: Budget, trigger: dict):
        """发送预算告警通知"""
        try:
            results = await self.notification_manager.send_budget_alert(
                webhook_url=budget.webhook_url,
                budget_name=budget.name,
                threshold=trigger["threshold"],
                current_percent=trigger["current_percent"],
                current_cost=trigger["current_cost"],
                budget_amount=budget.amount,
                period=budget.period
            )
            
            # 更新告警记录
            db = db_manager.get_session()
            alert = db.query(BudgetAlert).filter(
                BudgetAlert.budget_id == budget.id,
                BudgetAlert.threshold_percent == trigger["threshold"]
            ).order_by(BudgetAlert.created_at.desc()).first()
            
            if alert:
                alert.notification_sent = any(results.values())
                db.commit()
            
            db.close()
            
            info(logger, "Notification sent",
                 budget_id=budget.id,
                 results=results)
                 
        except Exception as e:
            error(logger, "Failed to send notification",
                  budget_id=budget.id,
                  error=str(e))


# 全局监控器实例
budget_monitor = BudgetMonitor()


async def start_budget_monitoring():
    """启动预算监控（后台任务）"""
    await budget_monitor.start_monitoring(interval_seconds=300)


def stop_budget_monitoring():
    """停止预算监控"""
    budget_monitor.stop_monitoring()