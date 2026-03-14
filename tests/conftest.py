"""
TokenMeter 测试配置和工具
"""
import pytest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API 响应"""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


@pytest.fixture
def sample_usage_record():
    """示例使用记录数据"""
    return {
        "request_id": "test-req-001",
        "provider": "openai",
        "model": "gpt-4",
        "prompt_tokens": 1000,
        "completion_tokens": 500,
        "total_tokens": 1500,
        "cost_input": 0.03,
        "cost_output": 0.03,
        "cost_total": 0.06,
        "project": "test-project",
        "team": "test-team",
        "environment": "test",
        "user_id": "test-user",
    }
