"""
Providers 模块单元测试
"""
import pytest
from src.proxy.providers import (
    create_provider,
    OpenAIProvider,
    AzureOpenAIProvider,
    AnthropicProvider,
    DashScopeProvider,
    ProviderConfig,
    PROVIDER_CLASSES,
)


class TestProviderFactory:
    """测试提供商工厂"""

    def test_create_openai_provider(self):
        """测试创建 OpenAI 提供商"""
        config = {"base_url": "https://api.openai.com"}
        provider = create_provider("openai", config)

        assert isinstance(provider, OpenAIProvider)
        assert provider.name == "openai"

    def test_create_azure_provider(self):
        """测试创建 Azure 提供商"""
        config = {"base_url": "https://test.openai.azure.com", "deployment": "gpt-4"}
        provider = create_provider("azure", config)

        assert isinstance(provider, AzureOpenAIProvider)
        assert provider.name == "azure"

    def test_create_anthropic_provider(self):
        """测试创建 Anthropic 提供商"""
        config = {"base_url": "https://api.anthropic.com"}
        provider = create_provider("anthropic", config)

        assert isinstance(provider, AnthropicProvider)
        assert provider.name == "anthropic"

    def test_create_claude_alias(self):
        """测试 Claude 别名"""
        config = {"base_url": "https://api.anthropic.com"}
        provider = create_provider("claude", config)

        assert isinstance(provider, AnthropicProvider)

    def test_create_dashscope_provider(self):
        """测试创建 DashScope 提供商"""
        config = {"base_url": "https://dashscope.aliyuncs.com/api/v1"}
        provider = create_provider("dashscope", config)

        assert isinstance(provider, DashScopeProvider)
        assert provider.name == "dashscope"

    def test_create_unknown_provider(self):
        """测试创建未知提供商应报错"""
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("unknown", {})


class TestOpenAIProvider:
    """测试 OpenAI 提供商"""

    def test_get_target_url(self):
        """测试获取目标 URL"""
        config = ProviderConfig(name="openai", base_url="https://api.openai.com")
        provider = OpenAIProvider(config)

        url = provider.get_target_url("/v1/chat/completions")
        assert url == "https://api.openai.com/v1/chat/completions"

    def test_extract_model(self):
        """测试提取模型名称"""
        config = ProviderConfig(name="openai", base_url="https://api.openai.com")
        provider = OpenAIProvider(config)

        body = {"model": "gpt-4", "messages": []}
        model = provider.extract_model(body)
        assert model == "gpt-4"

    def test_normalize_model_name(self):
        """测试模型名标准化"""
        config = ProviderConfig(name="openai", base_url="https://api.openai.com")
        provider = OpenAIProvider(config)

        # OpenAI 不需要标准化
        assert provider.normalize_model_name("gpt-4") == "gpt-4"


class TestAzureOpenAIProvider:
    """测试 Azure OpenAI 提供商"""

    def test_get_target_url_with_deployment(self):
        """测试获取带 deployment 的目标 URL"""
        config = ProviderConfig(
            name="azure", base_url="https://test.openai.azure.com", deployment="gpt-4-deployment"
        )
        provider = AzureOpenAIProvider(config)

        url = provider.get_target_url("/chat/completions", {"model": "gpt-4"})
        assert "openai/deployments/gpt-4/chat/completions" in url
        assert "test.openai.azure.com" in url

    def test_model_mapping(self):
        """测试模型名映射"""
        config = ProviderConfig(name="azure", base_url="https://test.openai.azure.com")
        provider = AzureOpenAIProvider(config)

        # Azure deployment 映射到标准模型名
        assert provider._azure_model_mapping("gpt-35-turbo") == "gpt-3.5-turbo"
        assert provider._azure_model_mapping("gpt-4o") == "gpt-4o"
        assert provider._azure_model_mapping("unknown") == "unknown"

    def test_prepare_headers_with_api_key(self):
        """测试准备请求头"""
        config = ProviderConfig(
            name="azure", base_url="https://test.openai.azure.com", api_key="test-key"
        )
        provider = AzureOpenAIProvider(config)

        headers = provider.prepare_headers({})
        assert headers["api-key"] == "test-key"


class TestAnthropicProvider:
    """测试 Anthropic 提供商"""

    def test_prepare_headers(self):
        """测试准备 Claude 请求头"""
        config = ProviderConfig(
            name="anthropic", base_url="https://api.anthropic.com", api_key="test-key"
        )
        provider = AnthropicProvider(config)

        headers = provider.prepare_headers({})
        assert headers["x-api-key"] == "test-key"
        assert headers["anthropic-version"] == "2023-06-01"

    def test_normalize_model_name(self):
        """测试 Claude 模型名标准化"""
        config = ProviderConfig(name="anthropic", base_url="https://api.anthropic.com")
        provider = AnthropicProvider(config)

        assert "claude-3-opus-20240229" in provider.normalize_model_name("claude-3-opus")
        assert "claude-3-sonnet-20240229" in provider.normalize_model_name(
            "claude-3-sonnet-20240229"
        )
        assert "claude-3-haiku-20240307" in provider.normalize_model_name("claude-3-haiku")


class TestDashScopeProvider:
    """测试 DashScope 提供商"""

    def test_prepare_headers(self):
        """测试准备 DashScope 请求头"""
        config = ProviderConfig(
            name="dashscope", base_url="https://dashscope.aliyuncs.com/api/v1", api_key="test-key"
        )
        provider = DashScopeProvider(config)

        headers = provider.prepare_headers({})
        assert headers["Authorization"] == "Bearer test-key"

    def test_normalize_model_name(self):
        """测试通义千问模型名标准化"""
        config = ProviderConfig(name="dashscope", base_url="https://dashscope.aliyuncs.com/api/v1")
        provider = DashScopeProvider(config)

        assert provider.normalize_model_name("qwen-max") == "qwen-max"
        assert provider.normalize_model_name("qwen-plus") == "qwen-plus"
        assert provider.normalize_model_name("qwen-turbo-123") == "qwen-turbo"


class TestProviderConfig:
    """测试提供商配置"""

    def test_config_creation(self):
        """测试配置创建"""
        config = ProviderConfig(
            name="test", base_url="https://test.com", api_key="secret", timeout=30
        )

        assert config.name == "test"
        assert config.base_url == "https://test.com"
        assert config.api_key == "secret"
        assert config.timeout == 30
