"""
TokenMeter Export Service
数据导出服务
"""
import csv
import io
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database.models import UsageRecord
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class ExportService:
    """数据导出服务"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def export_usage_records(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        project: Optional[str] = None,
        team: Optional[str] = None,
        provider: Optional[str] = None,
        format: str = "csv",
    ) -> tuple:
        """
        导出使用记录

        Returns:
            (content: str, filename: str, content_type: str)
        """
        # 构建查询
        query = self.db.query(UsageRecord)

        if start_date:
            query = query.filter(UsageRecord.timestamp >= start_date)
        if end_date:
            query = query.filter(UsageRecord.timestamp <= end_date)
        if project:
            query = query.filter(UsageRecord.project == project)
        if team:
            query = query.filter(UsageRecord.team == team)
        if provider:
            query = query.filter(UsageRecord.provider == provider)

        # 按时间排序
        records = query.order_by(UsageRecord.timestamp.desc()).all()

        if format.lower() == "csv":
            return self._export_to_csv(records)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_to_csv(self, records: List[UsageRecord]) -> tuple:
        """导出为 CSV 格式"""
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(
            [
                "ID",
                "Request ID",
                "Timestamp",
                "Provider",
                "Model",
                "Prompt Tokens",
                "Completion Tokens",
                "Total Tokens",
                "Input Cost (USD)",
                "Output Cost (USD)",
                "Total Cost (USD)",
                "Project",
                "Team",
                "Environment",
                "User ID",
                "Status Code",
                "Latency (ms)",
            ]
        )

        # 写入数据
        for record in records:
            writer.writerow(
                [
                    record.id,
                    record.request_id,
                    record.timestamp.isoformat() if record.timestamp else "",
                    record.provider,
                    record.model,
                    record.prompt_tokens,
                    record.completion_tokens,
                    record.total_tokens,
                    record.cost_input,
                    record.cost_output,
                    record.cost_total,
                    record.project,
                    record.team,
                    record.environment,
                    record.user_id,
                    record.status_code,
                    record.latency_ms,
                ]
            )

        content = output.getvalue()
        output.close()

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tokenmeter_usage_{timestamp}.csv"

        return content, filename, "text/csv"

    def export_summary_report(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> tuple:
        """
        导出汇总报告

        Returns:
            (content: str, filename: str, content_type: str)
        """
        from sqlalchemy import func

        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # 汇总统计
        summary = (
            self.db.query(
                UsageRecord.provider,
                UsageRecord.model,
                func.count(UsageRecord.id).label("request_count"),
                func.sum(UsageRecord.total_tokens).label("total_tokens"),
                func.sum(UsageRecord.cost_total).label("total_cost"),
            )
            .filter(UsageRecord.timestamp >= start_date, UsageRecord.timestamp <= end_date)
            .group_by(UsageRecord.provider, UsageRecord.model)
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)

        # 写入报告头部
        writer.writerow(["TokenMeter Usage Summary Report"])
        writer.writerow(["Generated at", datetime.now().isoformat()])
        writer.writerow(["Period", f"{start_date.date()} to {end_date.date()}"])
        writer.writerow([])

        # 写入汇总表
        writer.writerow(["Provider", "Model", "Request Count", "Total Tokens", "Total Cost (USD)"])

        total_cost = 0
        total_requests = 0

        for row in summary:
            writer.writerow(
                [
                    row.provider,
                    row.model,
                    row.request_count,
                    row.total_tokens,
                    round(row.total_cost, 6),
                ]
            )
            total_cost += row.total_cost
            total_requests += row.request_count

        writer.writerow([])
        writer.writerow(["TOTAL", "", total_requests, "", round(total_cost, 6)])

        content = output.getvalue()
        output.close()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tokenmeter_summary_{timestamp}.csv"

        return content, filename, "text/csv"
