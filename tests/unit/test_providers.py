"""
Providers 模块单元测试
测试多厂商适配器
"""
import pytest
from src.proxy.providers import (
    OpenAIProvider,
    AzureOpenAIProvider,
    AnthropicProvider,
    DashScopeProvider,
    create_provider,
    ProviderConfig,
)


class TestOpenAIProvider:
    """测试 OpenAI 提供商"""

    def test_get_target_url(self):
        """测试目标 URL 生成"""
        config = ProviderConfig(
            name="openai", base_url="https://api.openai.com/v1"
        )
        provider = OpenAIProvider(config)

        url = provider.get_target_url("/chat/completions")
        assert url == "https://api.openai.com/v1/chat/completions"

    def test_prepare_headers(self):
        """测试请求头准备"""
        config = ProviderConfig(name="openai", base_url="https://api.openai.com")
        provider = OpenAIProvider(config)

        headers = {"Authorization": "Bearer test-key", "Content-Type": "application/json"}
        result = provider.prepare_headers(headers)

        assert result["Authorization"] == "Bearer test-key"
        assert result["Content-Type"] == "application/json"

    def test_extract_model(self):
        """测试模型名称提取"""
        config = ProviderConfig(name="openai", base_url="https://api.openai.com")
        provider = OpenAIProvider(config)

        body = {"model": "gpt-4", "messages": []}
        model = provider.extract_model(body)
        assert model == "gpt-4"

    def test_extract_model_default(self):
        """测试默认模型名称"""
        config = ProviderConfig(name="openai", base_url="https://api.openai.com")
        provider = OpenAIProvider(config)

        body = {"messages": []}
        model = provider.extract_model(body)
        assert model == "unknown"

    def test_normalize_model_name(self):
        """测试模型名称标准化"""
        config = ProviderConfig(name="openai", base_url="https://api.openai.com")
        provider = OpenAIProvider(config)

        assert provider.normalize_model_name("gpt-4") == "gpt-4"
        assert provider.normalize_model_name("gpt-3.5-turbo") == "gpt-3.5-turbo"


class TestAzureOpenAIProvider:
    """测试 Azure OpenAI 提供商"""

    def test_get_target_url_chat_completions(self):
        """测试 Azure chat completions URL 生成"""
        config = ProviderConfig(
            name="azure",
            base_url="https://my-resource.openai.azure.com",
            deployment="gpt-4-deployment",
        )
        provider = AzureOpenAIProvider(config)

        url = provider.get_target_url("/chat/completions", {"model": "gpt-4"})
        assert "openai/deployments/gpt-4/chat/completions" in url

    def test_get_target_url_with_body_model(self):
        """测试从请求体获取 deployment"""
        config = ProviderConfig(
            name="azure",
            base_url="https://my-resource.openai.azure.com",
            deployment="default-deployment",
        )
        provider = AzureOpenAIProvider(config)

        url = provider.get_target_url("/chat/completions", {"model": "gpt-35-turbo"})
        assert "gpt-35-turbo" in url

    def test_prepare_headers_with_api_key(self):
        """测试 Azure 请求头准备"""
        config = ProviderConfig(
            name="azure",
            base_url="https://my-resource.openai.azure.com",
            api_key="azure-api-key",
        )
        provider = AzureOpenAIProvider(config)

        headers = {"Content-Type": "application/json"}
        result = provider.prepare_headers(headers)

        assert result["api-key"] == "azure-api-key"
        assert result["Content-Type"] == "application/json"

    def test_prepare_headers_with_existing_auth(self):
        """测试已有 Authorization 时不覆盖"""
        config = ProviderConfig(
            name="azure",
            base_url="https://my-resource.openai.azure.com",
            api_key="azure-api-key",
        )
        provider = AzureOpenAIProvider(config)

        headers = {"Authorization": "Bearer existing-token"}
        result = provider.prepare_headers(headers)

        assert "api-key" not in result

    def test_extract_model_with_deployment(self):
        """测试从 deployment 提取模型"""
        config = ProviderConfig(
            name="azure",
            base_url="https://my-resource.openai.azure.com",
            deployment="gpt-4-deployment",
        )
        provider = AzureOpenAIProvider(config)

        body = {"model": "gpt-4"}
        model = provider.extract_model(body)
        assert model == "gpt-4"

    def test_azure_model_mapping(self):
        """测试 Azure deployment 到模型映射"""
        config = ProviderConfig(name="azure", base_url="https://test.azure.com")
        provider = AzureOpenAIProvider(config)

        assert provider._azure_model_mapping("gpt-4") == "gpt-4"
        assert provider._azure_model_mapping("gpt-35-turbo") == "gpt-3.5-turbo"
        assert provider._azure_model_mapping("gpt-4o") == "gpt-4o"


class TestAnthropicProvider:
    """测试 Anthropic Claude 提供商"""

    def test_get_target_url(self):
        """测试目标 URL 生成"""
        config = ProviderConfig(
            name="anthropic", base_url="https://api.anthropic.com/v1"
        )
        provider = AnthropicProvider(config)

        url = provider.get_target_url("/messages")
        assert url == "https://api.anthropic.com/v1/messages"

    def test_prepare_headers(self):
        """测试 Claude 请求头准备"""
        config = ProviderConfig(
            name="anthropic",
            base_url="https://api.anthropic.com",
            api_key="claude-api-key",
            api_version="2023-06-01",
        )
        provider = AnthropicProvider(config)

        headers = {}
        result = provider.prepare_headers(headers)

        assert result["x-api-key"] == "claude-api-key"
        assert result["anthropic-version"] == "2023-06-01"

    def test_extract_model(self):
        """测试模型提取"""
        config = ProviderConfig(name="anthropic", base_url="https://api.anthropic.com")
        provider = AnthropicProvider(config)

        body = {"model": "claude-3-opus-20240229", "messages": []}
        model = provider.extract_model(body)
        assert model == "claude-3-opus-20240229"

    def test_extract_model_default(self):
        """测试默认模型"""
        config = ProviderConfig(name="anthropic", base_url="https://api.anthropic.com")
        provider = AnthropicProvider(config)

        body = {"messages": []}
        model = provider.extract_model(body)
        assert model == "claude-3-sonnet-20240229"

    def test_normalize_model_name(self):
        """测试模型名称标准化"""
        config = ProviderConfig(name="anthropic", base_url="https://api.anthropic.com")
        provider = AnthropicProvider(config)

        assert (
            provider.normalize_model_name("claude-3-opus")
            == "claude-3-opus-20240229"
        )
        assert (
            provider.normalize_model_name("claude-3-sonnet")
            == "claude-3-sonnet-20240229"
        )
        assert (
            provider.normalize_model_name("claude-3-haiku")
            == "claude-3-haiku-20240307"
        )


class TestDashScopeProvider:
    """测试阿里云 DashScope 提供商"""

    def test_get_target_url(self):
        """测试目标 URL 生成"""
        config = ProviderConfig(
            name="dashscope", base_url="https://dashscope.aliyuncs.com/api/v1"
        )
        provider = DashScopeProvider(config)

        url = provider.get_target_url("/services/aigc/text-generation/generation")
        assert "dashscope.aliyuncs.com" in url

    def test_prepare_headers(self):
        """测试请求头准备"""
        config = ProviderConfig(
            name="dashscope",
            base_url="https://dashscope.aliyuncs.com",
            api_key="dashscope-api-key",
        )
        provider = DashScopeProvider(config)

        headers = {}
        result = provider.prepare_headers(headers)

        assert result["Authorization"] == "Bearer dashscope-api-key"

    def test_extract_model(self):
        """测试模型提取"""
        config = ProviderConfig(
            name="dashscope", base_url="https://dashscope.aliyuncs.com"
        )
        provider = DashScopeProvider(config)

        body = {"model": "qwen-max", "input": {}}
        model = provider.extract_model(body)
        assert model == "qwen-max"

    def test_normalize_model_name(self):
        """测试模型名称标准化"""
        config = ProviderConfig(
            name="dashscope", base_url="https://dashscope.aliyuncs.com"
        )
        provider = DashScopeProvider(config)

        assert provider.normalize_model_name("qwen-max") == "qwen-max"
        assert provider.normalize_model_name("qwen-plus") == "qwen-plus"
        assert provider.normalize_model_name("qwen-turbo") == "qwen-turbo"


class TestProviderFactory:
    """测试提供商工厂"""

    def test_create_openai_provider(self):
        """测试创建 OpenAI 提供商"""
        provider = create_provider(
            "openai", {"base_url": "https://api.openai.com", "api_key": "test"}
        )
        assert isinstance(provider, OpenAIProvider)
        assert provider.name == "openai"

    def test_create_azure_provider(self):
        """测试创建 Azure 提供商"""
        provider = create_provider(
            "azure",
            {"base_url": "https://test.azure.com", "api_key": "test", "deployment": "gpt-4"},
        )
        assert isinstance(provider, AzureOpenAIProvider)

    def test_create_anthropic_provider(self):
        """测试创建 Anthropic 提供商"""
        provider = create_provider(
            "anthropic", {"base_url": "https://api.anthropic.com", "api_key": "test"}
        )
        assert isinstance(provider, AnthropicProvider)

    def test_create_claude_alias(self):
        """测试 claude 别名"""
        provider = create_provider(
            "claude", {"base_url": "https://api.anthropic.com", "api_key": "test"}
        )
        assert isinstance(provider, AnthropicProvider)

    def test_create_dashscope_provider(self):
        """测试创建 DashScope 提供商"""
        provider = create_provider(
            "dashscope",
            {"base_url": "https://dashscope.aliyuncs.com", "api_key": "test"},
        )
        assert isinstance(provider, DashScopeProvider)

    def test_create_tongyi_alias(self):
        """测试 tongyi 别名"""
        provider = create_provider(
            "tongyi",
            {"base_url": "https://dashscope.aliyuncs.com", "api_key": "test"},
        )
        assert isinstance(provider, DashScopeProvider)

    def test_create_unknown_provider(self):
        """测试未知提供商应报错"""
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("unknown", {"base_url": "https://test.com"})


class TestProviderConfig:
    """测试提供商配置"""

    def test_config_defaults(self):
        """测试配置默认值"""
        config = ProviderConfig(name="test", base_url="https://test.com")

        assert config.name == "test"
        assert config.base_url == "https://test.com"
        assert config.api_key is None
        assert config.api_version is None
        assert config.deployment is None
        assert config.timeout == 60
        assert config.max_retries == 3

    def test_config_custom_values(self):
        """测试自定义配置值"""
        config = ProviderConfig(
            name="test",
            base_url="https://test.com",
            api_key="secret",
            api_version="2024-01-01",
            deployment="gpt-4",
            timeout=120,
            max_retries=5,
        )

        assert config.api_key == "secret"
        assert config.api_version == "2024-01-01"
        assert config.deployment == "gpt-4"
        assert config.timeout == 120
        assert config.max_retries == 5
