"""
TokenMeter API Proxy
拦截并记录 API 请求 - 多厂商支持版本
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
from ..utils.logging_config import get_logger, info, error
from .providers import create_provider, BaseProvider

logger = get_logger(__name__)


class ProxyHandler:
    """代理处理器 - 支持多厂商"""
    
    def __init__(self, db_session: Session, provider_configs: Optional[Dict] = None):
        self.db = db_session
        self.client = httpx.AsyncClient(timeout=60.0)
        self.providers: Dict[str, BaseProvider] = {}
        
        # 初始化提供商
        self._init_providers(provider_configs or {})
    
    def _init_providers(self, configs: Dict):
        """初始化所有提供商"""
        # 默认配置
        default_configs = {
            "openai": {
                "base_url": "https://api.openai.com",
            },
            "azure": {
                "base_url": "https://your-resource.openai.azure.com",
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com",
            },
            "dashscope": {
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
            }
        }
        
        # 合并配置
        for provider_name, default_config in default_configs.items():
            user_config = configs.get(provider_name, {})
            merged_config = {**default_config, **user_config}
            
            try:
                provider = create_provider(provider_name, merged_config)
                self.providers[provider_name] = provider
                info(logger, f"Provider initialized", provider=provider_name)
            except Exception as e:
                error(logger, f"Failed to initialize provider", 
                      provider=provider_name, error=str(e))
    
    async def proxy_request(
        self,
        provider: str,
        request: Request,
        path: str = ""
    ) -> Response:
        """
        代理请求并记录用量
        
        Args:
            provider: 提供商名称 (openai, azure, anthropic, dashscope)
            request: FastAPI 请求对象
            path: API 路径
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())[:16]
        
        # 获取提供商实例
        provider_instance = self.providers.get(provider.lower())
        if not provider_instance:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown or disabled provider: {provider}"
            )
        
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
        target_url = provider_instance.get_target_url(path or request.url.path, body_json)
        
        # 构建转发头
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # 移除自定义标签头
        for key in list(headers.keys()):
            if key.lower().startswith("x-cost-"):
                headers.pop(key)
        
        # 提供商特定的头处理
        headers = provider_instance.prepare_headers(headers)
        
        try:
            info(logger, f"Proxy request started",
                 provider=provider,
                 method=request.method,
                 path=path,
                 target=target_url)
            
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
                provider_instance=provider_instance,
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
            
            info(logger, f"Proxy request completed",
                 provider=provider,
                 status_code=response.status_code,
                 latency_ms=latency_ms)
            
            return Response(
                content=content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except httpx.RequestError as e:
            error(logger, f"Proxy request failed",
                  provider=provider,
                  error=str(e))
            raise HTTPException(status_code=502, detail=f"Proxy error: {str(e)}")
    
    async def _record_usage(
        self,
        request_id: str,
        provider: str,
        provider_instance: BaseProvider,
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
        
        # 提取模型信息（使用提供商特定的方法）
        model = provider_instance.extract_model(body_json)
        model = provider_instance.normalize_model_name(model)
        
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
            cost_output=cost["output_cost"),
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
        
        info(logger, f"Usage recorded",
             request_id=request_id,
             provider=provider,
             model=model,
             tokens=total_tokens,
             cost=cost['total_cost'],
             project=project)
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
    
    def get_available_providers(self) -> list:
        """获取可用提供商列表"""
        return list(self.providers.keys())