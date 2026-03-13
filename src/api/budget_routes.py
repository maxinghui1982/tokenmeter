"""
TokenMeter Budget API Routes
预算管理 API 接口
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..database.models import get_db
from ..database.budget_models import Budget, BudgetAlert, BudgetCalculator, BudgetPeriod, BudgetScope
from ..utils.logging_config import get_logger, info, error

router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])
logger = get_logger(__name__)


# ============ Pydantic 模型 ============

class BudgetCreate(BaseModel):
    """创建预算请求模型"""
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    scope_type: str = Field(default="global")
    scope_value: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    period: str = Field(default="monthly")
    alert_thresholds: List[int] = Field(default=[50, 80, 100])
    webhook_url: Optional[str] = None
    email: Optional[str] = None


class BudgetUpdate(BaseModel):
    """更新预算请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    alert_thresholds: Optional[List[int]] = None
    webhook_url: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class BudgetResponse(BaseModel):
    """预算响应模型"""
    id: int
    name: str
    description: Optional[str]
    scope_type: str
    scope_value: Optional[str]
    amount: float
    currency: str
    period: str
    alert_thresholds: List[int]
    webhook_url: Optional[str]
    email: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class BudgetStatusResponse(BaseModel):
    """预算状态响应"""
    budget: BudgetResponse
    current_usage: float
    current_percent: float
    remaining: float
    period_start: str
    period_end: str


# ============ API 路由 ============

@router.post("", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    """创建预算"""
    import json
    
    try:
        db_budget = Budget(
            name=budget.name,
            description=budget.description,
            scope_type=budget.scope_type,
            scope_value=budget.scope_value,
            amount=budget.amount,
            currency=budget.currency,
            period=budget.period,
            alert_thresholds=json.dumps(budget.alert_thresholds),
            webhook_url=budget.webhook_url,
            email=budget.email,
        )
        
        db.add(db_budget)
        db.commit()
        db.refresh(db_budget)
        
        info(logger, "Budget created", budget_id=db_budget.id, name=db_budget.name)
        return db_budget.to_dict()
        
    except Exception as e:
        error(logger, "Failed to create budget", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[BudgetResponse])
async def list_budgets(
    scope_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """获取预算列表"""
    query = db.query(Budget)
    
    if scope_type:
        query = query.filter(Budget.scope_type == scope_type)
    if is_active is not None:
        query = query.filter(Budget.is_active == is_active)
    
    budgets = query.all()
    return [b.to_dict() for b in budgets]


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: int, db: Session = Depends(get_db)):
    """获取预算详情"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget.to_dict()


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: int, budget_update: BudgetUpdate, db: Session = Depends(get_db)):
    """更新预算"""
    import json
    
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    update_data = budget_update.dict(exclude_unset=True)
    
    if "alert_thresholds" in update_data:
        update_data["alert_thresholds"] = json.dumps(update_data["alert_thresholds"])
    
    for field, value in update_data.items():
        setattr(budget, field, value)
    
    db.commit()
    db.refresh(budget)
    
    info(logger, "Budget updated", budget_id=budget_id)
    return budget.to_dict()


@router.delete("/{budget_id}")
async def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """删除预算"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(budget)
    db.commit()
    
    info(logger, "Budget deleted", budget_id=budget_id)
    return {"success": True, "message": "Budget deleted"}


@router.get("/{budget_id}/status", response_model=BudgetStatusResponse)
async def get_budget_status(budget_id: int, db: Session = Depends(get_db)):
    """获取预算状态"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    calculator = BudgetCalculator(db)
    usage = calculator.calculate_current_usage(budget)
    
    current_cost = usage["total_cost"]
    current_percent = (current_cost / budget.amount * 100) if budget.amount > 0 else 0
    
    return {
        "budget": budget.to_dict(),
        "current_usage": current_cost,
        "current_percent": round(current_percent, 2),
        "remaining": round(budget.amount - current_cost, 4),
        "period_start": usage["period_start"].isoformat(),
        "period_end": usage["period_end"].isoformat(),
    }


@router.get("/{budget_id}/alerts")
async def get_budget_alerts(
    budget_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取预算告警历史"""
    alerts = db.query(BudgetAlert).filter(
        BudgetAlert.budget_id == budget_id
    ).order_by(BudgetAlert.created_at.desc()).limit(limit).all()
    
    return {
        "total": len(alerts),
        "alerts": [a.to_dict() for a in alerts]
    }


@router.post("/{budget_id}/check")
async def check_budget(budget_id: int, db: Session = Depends(get_db)):
    """手动触发预算检查"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    calculator = BudgetCalculator(db)
    triggered = calculator.check_budget_thresholds(budget)
    
    return {
        "budget_id": budget_id,
        "triggered_thresholds": triggered,
        "checked_at": datetime.utcnow().isoformat()
    }


@router.get("/summary/dashboard")
async def get_budget_summary(db: Session = Depends(get_db)):
    """获取预算汇总（仪表盘用）"""
    from sqlalchemy import func
    
    # 统计预算总数
    total_budgets = db.query(Budget).filter(Budget.is_active == True).count()
    
    # 统计告警数
    total_alerts = db.query(BudgetAlert).filter(
        BudgetAlert.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # 获取所有活跃预算的状态
    calculator = BudgetCalculator(db)
    budgets = db.query(Budget).filter(Budget.is_active == True).all()
    
    budget_statuses = []
    for budget in budgets:
        usage = calculator.calculate_current_usage(budget)
        current_percent = (usage["total_cost"] / budget.amount * 100) if budget.amount > 0 else 0
        
        budget_statuses.append({
            "id": budget.id,
            "name": budget.name,
            "amount": budget.amount,
            "used": usage["total_cost"],
            "percent": round(current_percent, 2),
            "status": "normal" if current_percent < 80 else "warning" if current_percent < 100 else "exceeded"
        })
    
    return {
        "total_budgets": total_budgets,
        "total_alerts_7d": total_alerts,
        "budgets": budget_statuses
    }


from datetime import datetime, timedelta