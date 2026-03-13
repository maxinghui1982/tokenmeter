"""
TokenMeter Notification Service
通知服务（飞书、钉钉、Slack）
"""
import json
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from ..utils.logging_config import get_logger, info, error

logger = get_logger(__name__)


class NotificationService:
    """通知服务基类"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_webhook(self, webhook_url: str, payload: Dict) -> bool:
        """发送 Webhook 通知"""
        try:
            response = await self.client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                info(logger, "Webhook notification sent", url=webhook_url[:50])
                return True
            else:
                error(logger, "Webhook notification failed",
                      status_code=response.status_code,
                      response=response.text[:200])
                return False
                
        except Exception as e:
            error(logger, "Webhook notification error", error=str(e))
            return False
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


class FeishuNotifier(NotificationService):
    """飞书通知器"""
    
    async def send_budget_alert(
        self,
        webhook_url: str,
        budget_name: str,
        threshold: int,
        current_percent: float,
        current_cost: float,
        budget_amount: float,
        period: str
    ) -> bool:
        """发送预算告警通知"""
        
        # 根据阈值设置颜色
        if threshold >= 100:
            color = "red"
            title = "🔴 预算已超支"
        elif threshold >= 80:
            color = "orange"
            title = "🟠 预算预警"
        else:
            color = "blue"
            title = "🔵 预算提醒"
        
        # 构建飞书卡片消息
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**预算名称**: {budget_name}\n**周期**: {period}"
                        }
                    },
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**当前使用**\n${current_cost:.4f}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**预算额度**\n${budget_amount:.4f}"
                                }
                            }
                        ]
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**使用率**: {current_percent:.1f}% (触发阈值: {threshold}%)"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": f"通知时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
        }
        
        return await self.send_webhook(webhook_url, payload)
    
    async def send_simple_text(
        self,
        webhook_url: str,
        text: str
    ) -> bool:
        """发送简单文本通知"""
        payload = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        return await self.send_webhook(webhook_url, payload)


class DingTalkNotifier(NotificationService):
    """钉钉通知器"""
    
    async def send_budget_alert(
        self,
        webhook_url: str,
        budget_name: str,
        threshold: int,
        current_percent: float,
        current_cost: float,
        budget_amount: float,
        period: str
    ) -> bool:
        """发送预算告警通知"""
        
        if threshold >= 100:
            title = "🔴 预算已超支"
        elif threshold >= 80:
            title = "🟠 预算预警"
        else:
            title = "🔵 预算提醒"
        
        # 钉钉 markdown 消息
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"### {title}\n\n"
                        f"**预算名称**: {budget_name}\n\n"
                        f"**周期**: {period}\n\n"
                        f"**当前使用**: ${current_cost:.4f}\n\n"
                        f"**预算额度**: ${budget_amount:.4f}\n\n"
                        f"**使用率**: {current_percent:.1f}% (触发阈值: {threshold}%)\n\n"
                        f"---\n"
                        f"通知时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
        
        return await self.send_webhook(webhook_url, payload)


class SlackNotifier(NotificationService):
    """Slack 通知器"""
    
    async def send_budget_alert(
        self,
        webhook_url: str,
        budget_name: str,
        threshold: int,
        current_percent: float,
        current_cost: float,
        budget_amount: float,
        period: str
    ) -> bool:
        """发送预算告警通知"""
        
        if threshold >= 100:
            color = "danger"
            title = "🔴 Budget Exceeded"
        elif threshold >= 80:
            color = "warning"
            title = "🟠 Budget Warning"
        else:
            color = "good"
            title = "🔵 Budget Notice"
        
        # Slack attachment
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "fields": [
                        {
                            "title": "Budget Name",
                            "value": budget_name,
                            "short": True
                        },
                        {
                            "title": "Period",
                            "value": period,
                            "short": True
                        },
                        {
                            "title": "Current Usage",
                            "value": f"${current_cost:.4f}",
                            "short": True
                        },
                        {
                            "title": "Budget Limit",
                            "value": f"${budget_amount:.4f}",
                            "short": True
                        },
                        {
                            "title": "Usage Percentage",
                            "value": f"{current_percent:.1f}% (Threshold: {threshold}%)",
                            "short": False
                        }
                    ],
                    "footer": "TokenMeter",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        return await self.send_webhook(webhook_url, payload)


class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self.feishu = FeishuNotifier()
        self.dingtalk = DingTalkNotifier()
        self.slack = SlackNotifier()
    
    async def send_budget_alert(
        self,
        webhook_url: str,
        budget_name: str,
        threshold: int,
        current_percent: float,
        current_cost: float,
        budget_amount: float,
        period: str
    ) -> Dict[str, bool]:
        """
        发送预算告警
        
        自动识别 webhook 类型并发送到对应平台
        """
        results = {}
        
        if "feishu" in webhook_url or "larksuite" in webhook_url:
            results["feishu"] = await self.feishu.send_budget_alert(
                webhook_url, budget_name, threshold, current_percent,
                current_cost, budget_amount, period
            )
        elif "dingtalk" in webhook_url or "dingtalk" in webhook_url:
            results["dingtalk"] = await self.dingtalk.send_budget_alert(
                webhook_url, budget_name, threshold, current_percent,
                current_cost, budget_amount, period
            )
        elif "slack" in webhook_url or "hooks.slack" in webhook_url:
            results["slack"] = await self.slack.send_budget_alert(
                webhook_url, budget_name, threshold, current_percent,
                current_cost, budget_amount, period
            )
        else:
            # 默认使用飞书格式
            results["feishu"] = await self.feishu.send_budget_alert(
                webhook_url, budget_name, threshold, current_percent,
                current_cost, budget_amount, period
            )
        
        return results
    
    async def close(self):
        """关闭所有通知器"""
        await self.feishu.close()
        await self.dingtalk.close()
        await self.slack.close()