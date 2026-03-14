"""
TokenMeter REST API
提供数据统计和查询接口
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.models import get_db, UsageRecord

router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/stats/summary")
async def get_summary(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """
    获取成本汇总统计

    Args:
        days: 统计天数（默认30天）
    """
    since = datetime.utcnow() - timedelta(days=days)

    # 总统计
    total_stats = (
        db.query(
            func.count(UsageRecord.id).label("total_requests"),
            func.sum(UsageRecord.total_tokens).label("total_tokens"),
            func.sum(UsageRecord.cost_total).label("total_cost"),
        )
        .filter(UsageRecord.timestamp >= since)
        .first()
    )

    # 按提供商统计
    provider_stats = (
        db.query(
            UsageRecord.provider,
            func.count(UsageRecord.id).label("requests"),
            func.sum(UsageRecord.total_tokens).label("tokens"),
            func.sum(UsageRecord.cost_total).label("cost"),
        )
        .filter(UsageRecord.timestamp >= since)
        .group_by(UsageRecord.provider)
        .all()
    )

    # 按模型统计
    model_stats = (
        db.query(
            UsageRecord.model,
            func.count(UsageRecord.id).label("requests"),
            func.sum(UsageRecord.total_tokens).label("tokens"),
            func.sum(UsageRecord.cost_total).label("cost"),
        )
        .filter(UsageRecord.timestamp >= since)
        .group_by(UsageRecord.model)
        .all()
    )

    return {
        "period_days": days,
        "summary": {
            "total_requests": total_stats.total_requests or 0,
            "total_tokens": total_stats.total_tokens or 0,
            "total_cost": round(total_stats.total_cost or 0, 4),
        },
        "by_provider": [
            {
                "provider": s.provider,
                "requests": s.requests,
                "tokens": s.tokens,
                "cost": round(s.cost, 4),
            }
            for s in provider_stats
        ],
        "by_model": [
            {"model": s.model, "requests": s.requests, "tokens": s.tokens, "cost": round(s.cost, 4)}
            for s in model_stats
        ],
    }


@router.get("/stats/projects")
async def get_project_stats(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """按项目统计成本"""
    since = datetime.utcnow() - timedelta(days=days)

    stats = (
        db.query(
            UsageRecord.project,
            func.count(UsageRecord.id).label("requests"),
            func.sum(UsageRecord.total_tokens).label("tokens"),
            func.sum(UsageRecord.cost_total).label("cost"),
        )
        .filter(UsageRecord.timestamp >= since)
        .group_by(UsageRecord.project)
        .order_by(func.sum(UsageRecord.cost_total).desc())
        .all()
    )

    return {
        "period_days": days,
        "projects": [
            {
                "project": s.project,
                "requests": s.requests,
                "tokens": s.tokens,
                "cost": round(s.cost, 4),
            }
            for s in stats
        ],
    }


@router.get("/stats/teams")
async def get_team_stats(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """按团队统计成本"""
    since = datetime.utcnow() - timedelta(days=days)

    stats = (
        db.query(
            UsageRecord.team,
            func.count(UsageRecord.id).label("requests"),
            func.sum(UsageRecord.total_tokens).label("tokens"),
            func.sum(UsageRecord.cost_total).label("cost"),
        )
        .filter(UsageRecord.timestamp >= since)
        .group_by(UsageRecord.team)
        .order_by(func.sum(UsageRecord.cost_total).desc())
        .all()
    )

    return {
        "period_days": days,
        "teams": [
            {"team": s.team, "requests": s.requests, "tokens": s.tokens, "cost": round(s.cost, 4)}
            for s in stats
        ],
    }


@router.get("/stats/daily")
async def get_daily_stats(
    days: int = Query(30, ge=1, le=365),
    project: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """按天统计成本趋势"""
    since = datetime.utcnow() - timedelta(days=days)

    query = db.query(
        func.date(UsageRecord.timestamp).label("date"),
        func.count(UsageRecord.id).label("requests"),
        func.sum(UsageRecord.total_tokens).label("tokens"),
        func.sum(UsageRecord.cost_total).label("cost"),
    ).filter(UsageRecord.timestamp >= since)

    if project:
        query = query.filter(UsageRecord.project == project)

    stats = (
        query.group_by(func.date(UsageRecord.timestamp))
        .order_by(func.date(UsageRecord.timestamp))
        .all()
    )

    return {
        "period_days": days,
        "project": project,
        "daily": [
            {
                "date": s.date.isoformat() if s.date else None,
                "requests": s.requests,
                "tokens": s.tokens,
                "cost": round(s.cost, 4),
            }
            for s in stats
        ],
    }


@router.get("/records")
async def get_records(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    project: Optional[str] = None,
    team: Optional[str] = None,
    provider: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取详细使用记录"""
    query = db.query(UsageRecord)

    if project:
        query = query.filter(UsageRecord.project == project)
    if team:
        query = query.filter(UsageRecord.team == team)
    if provider:
        query = query.filter(UsageRecord.provider == provider)

    total = query.count()
    records = query.order_by(UsageRecord.timestamp.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "records": [r.to_dict() for r in records],
    }
