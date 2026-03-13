# TokenMeter 🎫

> 企业级 MaaS 成本追踪与归因分析平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

**TokenMeter** 是一款开源的企业级 AI 成本管理工具，帮助企业追踪、归因和优化多源 MaaS（Model as a Service）支出。

## ✨ 核心特性

- 📊 **多源聚合** - 统一监控 OpenAI、Azure OpenAI、Claude、文心一言等主流 MaaS 提供商
- 🏷️ **精细归因** - 按项目、团队、环境、用户多维度标记和分摊成本
- ⚡ **实时监控** - 分钟级成本更新，告别月底账单惊吓
- 🚨 **智能预警** - 预算超支、用量突增、异常模式自动告警
- 📈 **财务级报表** - 支持成本分摊计算和财务导出
- 🔒 **隐私优先** - 支持本地化部署，数据不出企业

## 🎯 适用场景

| 场景 | 痛点 | TokenMeter 解决方案 |
|------|------|---------------------|
| 多业务线成本分摊 | 不知道哪个项目花了多少 | 按项目/API Key归因 |
| 预算管控 | 月底才知道超支 | 实时预算预警 |
| 多厂商管理 | 3个云厂商=3个账单 | 统一仪表盘 |
| 成本优化 | 不知道钱花在哪值不值 | 调用分析+优化建议 |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/tokenmeter.git
cd tokenmeter

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m src.database.init

# 启动服务
python -m src.main
```

### 配置代理

修改你的应用代码，将 API 请求指向 TokenMeter 代理：

```python
import openai

# 原来：直接调用 OpenAI
# openai.api_base = "https://api.openai.com/v1"

# 现在：通过 TokenMeter 代理
openai.api_base = "http://localhost:8080/proxy/openai"
openai.default_headers = {
    "X-Cost-Project": "customer-service-bot",
    "X-Cost-Team": "ai-platform",
    "X-Cost-Env": "production"
}
```

### 查看仪表盘

打开浏览器访问 `http://localhost:8080`，即可查看：

- 实时成本概览
- 项目维度分析
- 模型使用统计
- 预算执行情况

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        企业应用层                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ 客服机器人 │ │ 代码助手 │ │ 数据分析 │ │ 文档生成 │           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
└───────┼───────────┼───────────┼───────────┼─────────────────┘
        │           │           │           │
        └───────────┴─────┬─────┴───────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    TokenMeter Gateway                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 请求拦截  │ │ 用量记录  │ │ 成本计算  │ │ 流量转发  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   OpenAI     │ │ Azure OpenAI │ │    Claude    │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 📁 项目结构

```
tokenmeter/
├── src/
│   ├── proxy/          # API 代理层
│   ├── database/       # 数据模型与存储
│   ├── api/            # REST API
│   └── web/            # Web 仪表盘
├── config/             # 配置文件
├── docs/               # 文档
├── tests/              # 测试用例
└── examples/           # 使用示例
```

## 🔧 配置说明

创建 `config/config.yaml`：

```yaml
server:
  host: 0.0.0.0
  port: 8080

database:
  path: ./data/tokenmeter.db

providers:
  openai:
    base_url: https://api.openai.com/v1
    api_key: ${OPENAI_API_KEY}
  azure:
    base_url: https://your-resource.openai.azure.com
    api_key: ${AZURE_OPENAI_KEY}

budget:
  enabled: true
  alerts:
    - threshold: 80
      channels: [webhook]
    - threshold: 100
      channels: [webhook, email]
```

## 🛠️ 开发计划

- [x] 基础代理层
- [x] 成本统计核心
- [x] Web 仪表盘
- [ ] 多厂商支持扩展
- [ ] 预算预警系统
- [ ] SSO 集成
- [ ] 成本优化建议引擎

## 🤝 贡献指南

欢迎提交 Issue 和 PR！请先阅读 [CONTRIBUTING.md](docs/CONTRIBUTING.md)。

## 📄 许可证

[MIT License](LICENSE)

## 📬 联系我们

- 项目主页: https://github.com/yourusername/tokenmeter
- 问题反馈: https://github.com/yourusername/tokenmeter/issues
- 讨论区: https://github.com/yourusername/tokenmeter/discussions

---

**让每一分钱都花得明明白白** 💰
