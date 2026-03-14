"""
TokenMeter Export Routes
数据导出 API
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from ..database.models import get_db
from ..services.export_service import ExportService
from ..api.auth_routes import get_current_user
from ..database.user_models import User
from ..utils.logging_config import get_logger, info

router = APIRouter(prefix="/api/v1/export", tags=["export"])
logger = get_logger(__name__)


@router.get("/usage-records")
async def export_usage_records(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    project: Optional[str] = Query(None),
    team: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    format: str = Query("csv", regex="^(csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出使用记录"""
    try:
        # 解析日期
        start = None
        end = None
        if start_date:
            start = datetime.fromisoformat(start_date)
        if end_date:
            end = datetime.fromisoformat(end_date)

        service = ExportService(db)
        content, filename, content_type = service.export_usage_records(
            start_date=start,
            end_date=end,
            project=project,
            team=team,
            provider=provider,
            format=format,
        )

        info(
            logger,
            "Usage records exported",
            user_id=current_user.id,
            records_count=content.count("\n") - 1,
        )

        return PlainTextResponse(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary-report")
async def export_summary_report(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出汇总报告"""
    try:
        start = None
        end = None
        if start_date:
            start = datetime.fromisoformat(start_date)
        if end_date:
            end = datetime.fromisoformat(end_date)

        service = ExportService(db)
        content, filename, content_type = service.export_summary_report(
            start_date=start, end_date=end
        )

        info(logger, "Summary report exported", user_id=current_user.id)

        return PlainTextResponse(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
