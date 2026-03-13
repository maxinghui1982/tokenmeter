"""
Pricing 模块单元测试
"""
import pytest
from src.database.pricing import CostCalculator, calculator, DEFAULT_PRICING


class TestCostCalculator:
    """测试成本计算器"""
    
    def test_calculate_cost_gpt4(self):
        """测试 GPT-4 成本计算"""
        cost = calculator.calculate_cost(
            provider="openai",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        # GPT-4 定价: input $0.03/1K, output $0.06/1K
        assert cost["input_cost"] == 0.03
        assert cost["output_cost"] == 0.03  # 500/1000 * 0.06
        assert cost["total_cost"] == 0.06
    
    def test_calculate_cost_gpt35(self):
        """测试 GPT-3.5 成本计算"""
        cost = calculator.calculate_cost(
            provider="openai",
            model="gpt-3.5-turbo",
            prompt_tokens=2000,
            completion_tokens=1000
        )
        
        # GPT-3.5 定价: input $0.0005/1K, output $0.0015/1K
        assert cost["input_cost"] == 0.001
        assert cost["output_cost"] == 0.0015
        assert cost["total_cost"] == 0.0025
    
    def test_calculate_cost_embedding(self):
        """测试 Embedding 模型成本计算"""
        cost = calculator.calculate_cost(
            provider="openai",
            model="text-embedding-3-small",
            prompt_tokens=10000,
            completion_tokens=0
        )
        
        # Embedding 只有输入成本
        assert cost["input_cost"] == 0.0002
        assert cost["output_cost"] == 0.0
        assert cost["total_cost"] == 0.0002
    
    def test_calculate_cost_unknown_model(self):
        """测试未知模型应返回 0 成本"""
        cost = calculator.calculate_cost(
            provider="openai",
            model="unknown-model",
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        assert cost["input_cost"] == 0.0
        assert cost["output_cost"] == 0.0
        assert cost["total_cost"] == 0.0
    
    def test_calculate_cost_unknown_provider(self):
        """测试未知提供商应返回 0 成本"""
        cost = calculator.calculate_cost(
            provider="unknown-provider",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500
        )
        
        assert cost["total_cost"] == 0.0
    
    def test_fuzzy_match_model(self):
        """测试模型名称模糊匹配"""
        calc = CostCalculator()
        
        # 测试 GPT-4 变体
        pricing = calc._fuzzy_match_model("openai", "gpt-4-0613")
        assert pricing is not None
        
        # 测试 GPT-3.5 变体
        pricing = calc._fuzzy_match_model("openai", "gpt-3.5-turbo-16k")
        assert pricing is not None
    
    def test_get_model_pricing(self):
        """测试获取模型定价信息"""
        pricing = calculator.get_model_pricing("openai", "gpt-4")
        
        assert pricing is not None
        assert "input" in pricing
        assert "output" in pricing
        assert pricing["input"] == 0.03
        assert pricing["output"] == 0.06
    
    def test_list_available_models(self):
        """测试列出可用模型"""
        models = calculator.list_available_models()
        
        assert "openai" in models
        assert "azure" in models
        assert "claude" in models
        
        # 验证 OpenAI 模型列表
        openai_models = models["openai"]
        assert "gpt-4" in openai_models
        assert "gpt-3.5-turbo" in openai_models
    
    def test_list_available_models_filtered(self):
        """测试按提供商过滤模型列表"""
        models = calculator.list_available_models(provider="openai")
        
        assert len(models) == 1
        assert "openai" in models
    
    def test_custom_pricing(self):
        """测试自定义定价配置"""
        custom_pricing = {
            "custom": {
                "custom-model": {"input": 0.01, "output": 0.02}
            }
        }
        
        calc = CostCalculator(custom_pricing=custom_pricing)
        cost = calc.calculate_cost(
            provider="custom",
            model="custom-model",
            prompt_tokens=1000,
            completion_tokens=1000
        )
        
        assert cost["input_cost"] == 0.01
        assert cost["output_cost"] == 0.02
        assert cost["total_cost"] == 0.03


class TestDefaultPricing:
    """测试默认定价配置"""
    
    def test_default_pricing_structure(self):
        """测试默认定价结构完整性"""
        assert "openai" in DEFAULT_PRICING
        assert "azure" in DEFAULT_PRICING
        assert "claude" in DEFAULT_PRICING
    
    def test_openai_models_pricing(self):
        """测试 OpenAI 模型定价配置"""
        openai = DEFAULT_PRICING["openai"]
        
        # 检查主要模型
        assert "gpt-4" in openai
        assert "gpt-4-turbo" in openai
        assert "gpt-4o" in openai
        assert "gpt-4o-mini" in openai
        assert "gpt-3.5-turbo" in openai
        
        # 验证定价格式
        for model, pricing in openai.items():
            assert "input" in pricing
            assert "output" in pricing
            assert isinstance(pricing["input"], (int, float))
            assert isinstance(pricing["output"], (int, float))
            assert pricing["input"] >= 0
            assert pricing["output"] >= 0