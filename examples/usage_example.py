"""
TokenMeter Usage Example
展示如何将应用接入 TokenMeter 代理
"""

import os

# ==================== 示例 1: OpenAI ====================
def example_openai():
    """使用 OpenAI SDK 接入 TokenMeter"""
    import openai
    
    # 配置 TokenMeter 代理
    openai.api_base = "http://localhost:8080/proxy/openai/v1"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # 添加成本归因标签
    openai.default_headers = {
        "X-Cost-Project": "customer-service-bot",
        "X-Cost-Team": "ai-platform",
        "X-Cost-Env": "production",
        "X-Cost-User": "user-123"
    }
    
    # 正常调用 API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "你好，请介绍一下自己"}
        ]
    )
    
    print(f"回复: {response.choices[0].message.content}")
    print(f"Token 用量: {response.usage.total_tokens}")


# ==================== 示例 2: 直接 HTTP 请求 ====================
def example_http_request():
    """使用原始 HTTP 请求接入 TokenMeter"""
    import requests
    
    url = "http://localhost:8080/proxy/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json",
        # TokenMeter 归因标签
        "X-Cost-Project": "code-assistant",
        "X-Cost-Team": "developer-tools",
        "X-Cost-Env": "staging"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "写一个 Python 函数计算斐波那契数列"}
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    print(f"回复: {result['choices'][0]['message']['content']}")


# ==================== 示例 3: LangChain ====================
def example_langchain():
    """使用 LangChain 接入 TokenMeter"""
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    
    # 配置 LangChain 使用 TokenMeter 代理
    llm = ChatOpenAI(
        model_name="gpt-4",
        openai_api_base="http://localhost:8080/proxy/openai/v1",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_kwargs={
            "headers": {
                "X-Cost-Project": "document-analysis",
                "X-Cost-Team": "data-science"
            }
        }
    )
    
    result = llm.predict("总结这段话的要点...")
    print(result)


# ==================== 示例 4: 批量调用 ====================
def example_batch_calls():
    """批量调用并追踪成本"""
    import openai
    
    openai.api_base = "http://localhost:8080/proxy/openai/v1"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    tasks = [
        {"project": "content-generation", "prompt": "写一篇关于AI的文章"},
        {"project": "translation", "prompt": "把这句话翻译成法语"},
        {"project": "summarization", "prompt": "总结这篇论文"},
    ]
    
    for task in tasks:
        openai.default_headers = {
            "X-Cost-Project": task["project"],
            "X-Cost-Team": "nlp-team"
        }
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": task["prompt"]}]
        )
        
        print(f"✅ {task['project']}: {response.usage.total_tokens} tokens")


if __name__ == "__main__":
    print("TokenMeter 使用示例")
    print("=" * 50)
    print("\n请先确保 TokenMeter 服务已启动:")
    print("  python -m src.main")
    print("\n然后运行示例代码，查看仪表盘: http://localhost:8080")
    print("=" * 50)
    
    # 取消注释你想运行的示例
    # example_openai()
    # example_http_request()
    # example_langchain()
    # example_batch_calls()