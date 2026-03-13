"""
TokenMeter API Proxy
拦截并记录 API 请求
"""
import json
import uuid
import time
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from sqlalchemy.orm import Session

from ..database.models import UsageRecord
from ..database.pricing import calculator


class ProxyHandler:
    """代理处理器"""
    
    # 支持的提供商配置
    PROVIDERS = {
        "openai": {
            "base_url": "https://api.openai.com",
            "chat_endpoint": "/v1/chat/completions",
            "models_endpoint": "/v1/models",
        },
        "azure": {
            "base_url": None,  # 需要用户配置
            "chat_endpoint": "/openai/deployments/{deployment}/chat/completions",
        },
    }
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def proxy_request(
        self,
        provider: str,
        request: Request,
        path: str = ""
    ) -> Response:
        """
        代理请求并记录用量
        
        Args:
            provider: 提供商名称 (openai, azure, etc.)
            request: FastAPI 请求对象
            path: API 路径
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())[:16]
        
        # 获取请求头中的归因标签
        project = request.headers.get("X-Cost-Project", "default")
        team = request.headers.get("X-Cost-Team", "default")
        environment = request.headers.get("X-Cost-Env", "production")
        user_id = request.headers.get("X-Cost-User", "anonymous")
        
        # 读取请求体
        body = await request.body()
        body_json = {}
        try:
            body_json = json.loads(body) if body else {}
        except:
            pass
        
        # 获取目标 URL
        target_url = await self._get_target_url(provider, path, body_json)
        
        # 构建转发头（过滤掉归因标签）
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # 移除自定义标签头
        for key in list(headers.keys()):
            if key.lower().startswith("x-cost-"):
                headers.pop(key)
        
        try:
            # 转发请求
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # 解析响应并记录用量
            await self._record_usage(
                request_id=request_id,
                provider=provider,
                request_path=path or request.url.path,
                body_json=body_json,
                response=response,
                project=project,
                team=team,
                environment=environment,
                user_id=user_id,
                latency_ms=latency_ms
            )
            
            # 返回响应
            content = await response.aread()
            return Response(
                content=content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Proxy error: {str(e)}")
    
    async def _get_target_url(
        self, 
        provider: str, 
        path: str,
        body_json: Dict
    ) -> str:
        """获取目标 URL"""
        config = self.PROVIDERS.get(provider, {})
        
        if provider == "openai":
            base_url = config.get("base_url")
            return f"{base_url}{path}"
        
        elif provider == "azure":
            # Azure 需要特殊处理 deployment
            base_url = config.get("base_url") or "https://your-resource.openai.azure.com"
            # 可以从环境变量或配置读取
            return f"{base_url}{path}"
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    
    async def _record_usage(
        self,
        request_id: str,
        provider: str,
        request_path: str,
        body_json: Dict,
        response: httpx.Response,
        project: str,
        team: str,
        environment: str,
        user_id: str,
        latency_ms: int
    ):
        """记录 API 用量"""
        # 只记录 chat completions 请求
        if "chat/completions" not in request_path:
            return
        
        try:
            response_data = response.json() if response.status_code == 200 else {}
        except:
            response_data = {}
        
        # 提取模型信息
        model = body_json.get("model", "unknown")
        
        # 提取 token 用量
        usage = response_data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        
        # 计算成本
        cost = calculator.calculate_cost(
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )
        
        # 创建记录
        record = UsageRecord(
            request_id=request_id,
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_input=cost["input_cost"],
            cost_output=cost["output_cost"],
            cost_total=cost["total_cost"],
            project=project,
            team=team,
            environment=environment,
            user_id=user_id,
            request_path=request_path,
            status_code=response.status_code,
            latency_ms=latency_ms
        )
        
        self.db.add(record)
        self.db.commit()
        
        # 打印日志（调试用）
        print(f"📊 Recorded: {request_id} | {provider}/{model} | "
              f"Tokens: {total_tokens} | Cost: ${cost['total_cost']:.6f} | "
              f"Project: {project}")
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()