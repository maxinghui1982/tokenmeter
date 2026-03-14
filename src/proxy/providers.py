"""
TokenMeter 提供商基类
支持多厂商 MaaS 服务
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class ProviderConfig:
    """提供商配置"""

    name: str
    base_url: str
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    deployment: Optional[str] = None  # Azure 专用

    # 可选配置
    timeout: int = 60
    max_retries: int = 3


class BaseProvider(ABC):
    """MaaS 提供商基类"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = config.name

    @abstractmethod
    def get_target_url(self, path: str, body_json: Dict = None) -> str:
        """
        获取目标 URL

        Args:
            path: API 路径
            body_json: 请求体（用于 Azure 等需要动态路由的场景）

        Returns:
            完整的目标 URL
        """
        pass

    @abstractmethod
    def prepare_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        准备转发请求头

        Args:
            headers: 原始请求头

        Returns:
            处理后的请求头
        """
        pass

    @abstractmethod
    def extract_model(self, body_json: Dict) -> str:
        """
        从请求体中提取模型名称

        Args:
            body_json: 请求体

        Returns:
            模型名称
        """
        pass

    @abstractmethod
    def normalize_model_name(self, model: str) -> str:
        """
        标准化模型名称（用于成本计算）

        Args:
            model: 原始模型名称

        Returns:
            标准化的模型名称
        """
        return model


class OpenAIProvider(BaseProvider):
    """OpenAI 提供商"""

    def get_target_url(self, path: str, body_json: Dict = None) -> str:
        return f"{self.config.base_url}{path}"

    def prepare_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        # OpenAI 直接转发，无需特殊处理
        return headers

    def extract_model(self, body_json: Dict) -> str:
        return body_json.get("model", "unknown")

    def normalize_model_name(self, model: str) -> str:
        # OpenAI 模型名已经是标准格式
        return model


class AzureOpenAIProvider(BaseProvider):
    """Azure OpenAI 提供商"""

    def get_target_url(self, path: str, body_json: Dict = None) -> str:
        """
        Azure 路由规则：
        /openai/deployments/{deployment}/chat/completions
        """
        if "chat/completions" in path:
            # 从请求体或配置获取 deployment
            deployment = self.config.deployment
            if body_json and "model" in body_json:
                deployment = body_json["model"]

            # 构建 Azure 格式路径
            azure_path = f"/openai/deployments/{deployment}/chat/completions"
            return f"{self.config.base_url}{azure_path}"

        return f"{self.config.base_url}{path}"

    def prepare_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        # Azure 需要 api-key 而不是 Authorization Bearer
        if self.config.api_key and "authorization" not in [k.lower() for k in headers.keys()]:
            headers["api-key"] = self.config.api_key
        return headers

    def extract_model(self, body_json: Dict) -> str:
        # Azure 用 deployment 作为模型标识
        model = body_json.get("model", self.config.deployment or "unknown")
        # 映射回标准模型名
        return self._azure_model_mapping(model)

    def normalize_model_name(self, model: str) -> str:
        return self._azure_model_mapping(model)

    def _azure_model_mapping(self, deployment: str) -> str:
        """Azure deployment 到标准模型名的映射"""
        # 常见映射规则
        mapping = {
            "gpt-4": "gpt-4",
            "gpt-4-32k": "gpt-4-32k",
            "gpt-35-turbo": "gpt-3.5-turbo",
            "gpt-35-turbo-16k": "gpt-3.5-turbo-16k",
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini",
        }
        return mapping.get(deployment, deployment)


class AnthropicProvider(BaseProvider):
    """Anthropic Claude 提供商"""

    def get_target_url(self, path: str, body_json: Dict = None) -> str:
        return f"{self.config.base_url}{path}"

    def prepare_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        # Claude 需要 x-api-key 头
        if self.config.api_key:
            headers["x-api-key"] = self.config.api_key
            headers["anthropic-version"] = self.config.api_version or "2023-06-01"
        return headers

    def extract_model(self, body_json: Dict) -> str:
        return body_json.get("model", "claude-3-sonnet-20240229")

    def normalize_model_name(self, model: str) -> str:
        # Claude 模型名标准化
        if "claude-3-opus" in model:
            return "claude-3-opus-20240229"
        elif "claude-3-sonnet" in model:
            return "claude-3-sonnet-20240229"
        elif "claude-3-haiku" in model:
            return "claude-3-haiku-20240307"
        return model


class DashScopeProvider(BaseProvider):
    """阿里云 DashScope（通义千问）提供商"""

    def get_target_url(self, path: str, body_json: Dict = None) -> str:
        return f"{self.config.base_url}{path}"

    def prepare_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        # DashScope 需要 Authorization: Bearer {api_key}
        if self.config.api_key and "authorization" not in [k.lower() for k in headers.keys()]:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def extract_model(self, body_json: Dict) -> str:
        return body_json.get("model", "qwen-turbo")

    def normalize_model_name(self, model: str) -> str:
        # 通义千问模型名标准化
        if "qwen-max" in model:
            return "qwen-max"
        elif "qwen-plus" in model:
            return "qwen-plus"
        elif "qwen-turbo" in model:
            return "qwen-turbo"
        return model


# 提供商工厂
PROVIDER_CLASSES = {
    "openai": OpenAIProvider,
    "azure": AzureOpenAIProvider,
    "anthropic": AnthropicProvider,
    "claude": AnthropicProvider,
    "dashscope": DashScopeProvider,
    "tongyi": DashScopeProvider,
}


def create_provider(provider_name: str, config: Dict[str, Any]) -> BaseProvider:
    """
    创建提供商实例

    Args:
        provider_name: 提供商名称
        config: 配置字典

    Returns:
        提供商实例
    """
    provider_class = PROVIDER_CLASSES.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")

    provider_config = ProviderConfig(
        name=provider_name,
        base_url=config.get("base_url", ""),
        api_key=config.get("api_key"),
        api_version=config.get("api_version"),
        deployment=config.get("deployment"),
        timeout=config.get("timeout", 60),
        max_retries=config.get("max_retries", 3),
    )

    return provider_class(provider_config)
