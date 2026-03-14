"""
TokenMeter Cost Calculator
计算各模型的成本
"""
from typing import Dict, Optional

# 默认定价（美元 per 1K tokens）
# 注意：实际价格请以各厂商最新公布为准
DEFAULT_PRICING = {
    "openai": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-32k": {"input": 0.06, "output": 0.12},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-16k": {"input": 0.001, "output": 0.002},
        "text-embedding-3-small": {"input": 0.00002, "output": 0},
        "text-embedding-3-large": {"input": 0.00013, "output": 0},
    },
    "azure": {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-32k": {"input": 0.06, "output": 0.12},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-35-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-35-turbo-16k": {"input": 0.001, "output": 0.002},
    },
    "claude": {
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        "claude-2.1": {"input": 0.008, "output": 0.024},
        "claude-2.0": {"input": 0.008, "output": 0.024},
    },
    "anthropic": {
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    },
    "dashscope": {
        "qwen-max": {"input": 0.003, "output": 0.009},
        "qwen-plus": {"input": 0.001, "output": 0.002},
        "qwen-turbo": {"input": 0.0005, "output": 0.001},
    },
    "tongyi": {
        "qwen-max": {"input": 0.003, "output": 0.009},
        "qwen-plus": {"input": 0.001, "output": 0.002},
        "qwen-turbo": {"input": 0.0005, "output": 0.001},
    },
}


class CostCalculator:
    """成本计算器"""

    def __init__(self, custom_pricing: Optional[Dict] = None):
        self.pricing = custom_pricing or DEFAULT_PRICING

    def calculate_cost(
        self, provider: str, model: str, prompt_tokens: int, completion_tokens: int
    ) -> Dict[str, float]:
        """
        计算单次调用的成本

        Returns:
            {
                "input_cost": float,    # 输入成本
                "output_cost": float,   # 输出成本
                "total_cost": float     # 总成本
            }
        """
        # 获取模型定价
        provider_pricing = self.pricing.get(provider.lower(), {})
        model_pricing = provider_pricing.get(model, {})

        # 如果没找到定价，尝试模糊匹配
        if not model_pricing:
            model_pricing = self._fuzzy_match_model(provider, model)

        if not model_pricing:
            # 使用默认定价或返回0
            return {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0}

        # 计算成本（价格 per 1K tokens）
        input_cost = (prompt_tokens / 1000) * model_pricing.get("input", 0)
        output_cost = (completion_tokens / 1000) * model_pricing.get("output", 0)

        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(input_cost + output_cost, 6),
        }

    def _fuzzy_match_model(self, provider: str, model: str) -> Optional[Dict]:
        """模糊匹配模型名称"""
        provider_pricing = self.pricing.get(provider.lower(), {})

        # 尝试前缀匹配
        for model_key, pricing in provider_pricing.items():
            if model.startswith(model_key) or model_key in model:
                return pricing

        return None

    def get_model_pricing(self, provider: str, model: str) -> Optional[Dict]:
        """获取模型定价信息"""
        provider_pricing = self.pricing.get(provider.lower(), {})
        return provider_pricing.get(model)

    def list_available_models(self, provider: Optional[str] = None) -> Dict:
        """列出可用的模型定价"""
        if provider:
            return {provider: self.pricing.get(provider.lower(), {})}
        return self.pricing


# 全局实例
calculator = CostCalculator()
