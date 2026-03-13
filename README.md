# TokenMeter 🎫

> 企业级 MaaS 成本追踪与归因分析平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

**TokenMeter** 是一款开源的企业级 AI 成本管理工具，帮助企业追踪、归因和优化多源 MaaS（Model as a Service）支出。

📖 **开源策略**: 核心功能完全开源（MIT），高级功能（SSO、高级报表、企业级支持）提供商业授权。

---

## ✨ 核心特性

- 📊 **多源聚合** - 统一监控 OpenAI、Azure OpenAI、Claude、通义千问等主流 MaaS 提供商
- 🏷️ **精细归因** - 按项目、团队、环境、用户多维度标记和分摊成本
- ⚡ **实时监控** - 分钟级成本更新，告别月底账单惊吓
- 🚨 **智能预警** - 预算超支、用量突增、异常模式自动告警
- 📈 **财务级报表** - 支持成本分摊计算和财务导出
- 🔒 **隐私优先** - 支持本地化部署，数据不出企业
- 🚀 **飞书集成** - 原生支持飞书 webhook 通知

---

## 🎯 适用场景

| 场景 | 痛点 | TokenMeter 解决方案 |
|------|------|---------------------|
| 多业务线成本分摊 | 不知道哪个项目花了多少 | 按项目/API Key归因 |
| 预算管控 | 月底才知道超支 | 实时预算预警 |
| 多厂商管理 | 3个云厂商=3个账单 | 统一仪表盘 |
| 成本优化 | 不知道钱花在哪值不值 | 调用分析+优化建议 |

---

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/mxinghui/tokenmeter.git
cd tokenmeter

# 2. 启动服务
docker-compose up -d

# 3. 访问仪表盘
open http://localhost:8080
```

### 方式二：源码安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python -m src.database.init

# 3. 启动服务
python -m src.main
```

### 配置代理

修改你的应用代码，将 API 请求指向 TokenMeter 代理：

```python
import openai

# 配置 TokenMeter 代理
openai.api_base = "http://localhost:8080/proxy/openai/v1"
openai.default_headers = {
    "X-Cost-Project": "customer-service-bot",
    "X-Cost-Team": "ai-platform",
    "X-Cost-Env": "production"
}

# 正常调用，成本自动追踪
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

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

---

## 📁 项目结构

```
tokenmeter/
├── src/
│   ├── proxy/          # API 代理层
│   ├── database/       # 数据模型与存储
│   ├── api/            # REST API
│   ├── web/            # Web 仪表盘
│   └── auth/           # 认证与权限（开源版基础功能）
├── config/             # 配置文件
├── docs/               # 文档
├── tests/              # 测试用例
├── docker/             # Docker 配置
└── examples/           # 使用示例
```

---

## 🔧 功能对比

| 功能 | 开源版 | 企业版 |
|------|--------|--------|
| 多厂商成本追踪 | ✅ | ✅ |
| Web 仪表盘 | ✅ | ✅ |
| 预算预警 | ✅ | ✅ |
| 飞书/钉钉通知 | ✅ | ✅ |
| 数据导出 | ✅ | ✅ |
| 用户管理 | ✅ 基础 | ✅ 高级 RBAC |
| SSO/LDAP | ❌ | ✅ |
| 高级报表 | ❌ | ✅ |
| 企业级支持 | ❌ | ✅ |

**企业版咨询**: contact@tokenmeter.io

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！请先阅读 [CONTRIBUTING.md](docs/CONTRIBUTING.md)。

---

## 📄 许可证

[MIT License](LICENSE) - 核心功能完全开源

---

## 📬 联系我们

- 项目主页: https://github.com/mxinghui/tokenmeter
- 问题反馈: https://github.com/mxinghui/tokenmeter/issues
- 商务咨询: contact@tokenmeter.io

---

**让每一分钱都花得明明白白** 💰
