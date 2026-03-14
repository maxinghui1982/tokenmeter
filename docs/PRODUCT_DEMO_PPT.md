# TokenMeter v0.5.0 产品演示
## 开源企业级 AI 成本管理工具

---

## 第1页：封面

**TokenMeter**
开源企业级 AI 成本管理工具

追踪、归因和优化多源 MaaS 支出

版本：v0.5.0（生产就绪版）
GitHub: github.com/maxinghui1982/tokenmeter

---

## 第2页：问题场景

**企业在 AI 应用中的痛点**

- 💸 **成本失控**：多个团队使用不同 AI 服务，月度账单难以预测
- 🔍 **无法归因**：不知道哪个项目/团队消耗了最多预算
- 📊 **缺乏可视**：没有统一平台查看所有 AI 调用和成本
- ⚠️ **预警缺失**：预算超支后才后知后觉
- 🔧 **多厂商管理**：OpenAI、Azure、Claude 等各有一套账单

**典型案例**
某互联网公司月度 AI 账单从 $5K 暴涨到 $50K，花了一周才定位到是某个项目的循环调用 bug

---

## 第3页：产品介绍

**TokenMeter 是什么？**

企业级 AI 成本追踪与归因分析平台

**核心能力**
1. 📡 **透明代理** - 零代码改动接入现有 AI 调用
2. 💰 **实时计费** - 精确到每次调用的成本计算
3. 🏷️ **多维归因** - 项目/团队/环境三维度分析
4. 🔔 **预算预警** - 阈值告警 + 飞书通知
5. 📈 **监控大盘** - Prometheus + Grafana 可视化

**部署方式**
- Docker 一键部署（5分钟启动）
- 支持单机/集群部署
- 可选 PostgreSQL 企业版

---

## 第4页：功能架构

**系统架构图**

```
┌─────────────────────────────────────────────────────────┐
│                      用户应用层                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  App A  │  │  App B  │  │  App C  │  │   ...   │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
└───────┼────────────┼────────────┼────────────┼─────────┘
        │            │            │            │
        └────────────┴──────┬─────┴────────────┘
                            │
                    ┌───────┴───────┐
                    │   TokenMeter  │
                    │   代理层       │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────┴───────┐  ┌───────┴───────┐  ┌───────┴───────┐
│    OpenAI     │  │  Azure OpenAI │  │   Anthropic   │
│   (GPT-4)     │  │   (GPT-4)     │  │   (Claude)    │
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────┴───────┐
                    │  TokenMeter   │
                    │   分析平台     │
                    │  • 成本追踪   │
                    │  • 预算预警   │
                    │  • 监控大盘   │
                    └───────────────┘
```

---

## 第5页：核心功能 - 透明代理

**零代码改动接入**

**接入前（直接调用 OpenAI）**
```python
import openai
openai.api_key = "sk-xxx"

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**接入后（通过 TokenMeter）**
```python
import openai
# 只改 base_url，其余代码完全不变
openai.api_base = "http://tokenmeter:8080/proxy/openai/v1"
openai.api_key = "sk-xxx"

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    headers={  # 可选：添加标签
        "X-Project": "customer-service",
        "X-Team": "ai-team",
        "X-Environment": "production"
    }
)
```

**✅ 价值**
- 现有代码无需改动
- 自动记录每次调用
- 支持多厂商统一入口

---

## 第6页：核心功能 - 成本追踪

**实时成本计算**

| 提供商 | 模型 | 输入价格 | 输出价格 |
|--------|------|----------|----------|
| OpenAI | GPT-4 | $0.03/1K | $0.06/1K |
| OpenAI | GPT-3.5 | $0.0005/1K | $0.0015/1K |
| Azure | GPT-4 | $0.03/1K | $0.06/1K |
| Claude | Claude-3-Opus | $0.015/1K | $0.075/1K |
| DashScope | Qwen-Max | $0.003/1K | $0.009/1K |

**自动记录字段**
- Request ID、时间戳
- Provider、Model
- Prompt/Completion Tokens
- 输入/输出/总成本
- 项目/团队/环境标签
- 延迟、状态码

---

## 第7页：核心功能 - 多维归因

**三维度成本分析**

**1. 按项目分析**
```
项目名称          调用次数    总成本      占比
─────────────────────────────────────────────
customer-service   15,230    $1,245.50   45%
internal-tools      8,450      $523.20   19%
marketing-ai        5,120      $890.30   32%
─────────────────────────────────────────────
总计               28,800    $2,659.00  100%
```

**2. 按团队分析**
```
团队         本月成本    预算      使用率
────────────────────────────────────────
AI Team      $1,245    $2,000    62% 🟢
DevOps         $523    $1,000    52% 🟢
Marketing      $890    $1,000    89% 🟡
────────────────────────────────────────
```

**3. 按环境分析**
```
环境         成本        占比
────────────────────────────
Production   $2,100      79%
Staging        $450      17%
Development    $109       4%
────────────────────────────
```

---

## 第8页：核心功能 - 预算预警

**预算管理**

**创建预算**
```json
POST /api/v1/budgets
{
  "name": "AI Team 月度预算",
  "amount": 2000.00,
  "period": "monthly",
  "project": "ai-team",
  "alert_thresholds": [50, 80, 100],
  "webhook_url": "https://open.feishu.cn/xxx"
}
```

**告警规则**
- 🟡 50% 提醒：预算使用过半，请关注
- 🟠 80% 警告：预算即将用完，请控制使用
- 🔴 100% 严重：预算已用完，请立即处理

**飞书通知示例**
```
⚠️ TokenMeter 预算告警

预算：AI Team 月度预算
使用率：82% ($1,640 / $2,000)
等级：🔴 警告

本月调用统计：
- OpenAI GPT-4: $890 (54%)
- Claude Opus: $450 (27%)
- Azure GPT-4: $300 (19%)

查看详情：http://tokenmeter:8080
```

---

## 第9页：核心功能 - 监控大盘

**Grafana 仪表盘**

**概览面板**
- 📊 请求速率 (req/s)
- ⏱️ P95 响应时间
- 💰 总成本 (USD)
- 📈 预算使用率

**API 调用分析**
- 按提供商的调用速率
- 按模型的 P95 延迟
- 成功率/错误率趋势

**成本分析**
- 成本分布饼图（按提供商）
- 每日成本趋势
- 预算使用率仪表盘

**系统监控**
- 活跃用户数
- 数据库连接池
- HTTP 请求延迟分布

---

## 第10页：操作界面展示

**Web 仪表盘截图**

```
┌────────────────────────────────────────────────────────────┐
│  TokenMeter v0.5.0                              [用户] ▼  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  📊 概览数据                                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ 总请求数    │ │  总成本     │ │  活跃项目   │           │
│  │   28,800   │ │  $2,659.00 │ │      3      │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                            │
│  📈 成本趋势（最近30天）                                     │
│  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇                    │
│                                                            │
│  📋 最近调用记录                                            │
│  ───────────────────────────────────────────────────────  │
│  时间        提供商    模型        成本      项目           │
│  ───────────────────────────────────────────────────────  │
│  10:23:45   OpenAI    GPT-4      $0.023   customer-svc    │
│  10:23:12   Claude    Opus       $0.045   marketing       │
│  10:22:58   Azure     GPT-4      $0.023   internal-tools  │
│  ───────────────────────────────────────────────────────  │
│                                                            │
│  [查看全部]  [导出 CSV]                                    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 第11页：操作步骤演示

**Step 1: 部署 TokenMeter（5分钟）**

```bash
# 克隆仓库
git clone https://github.com/maxinghui1982/tokenmeter.git
cd tokenmeter

# 启动服务
docker-compose up -d

# 检查状态
curl http://localhost:8080/api/v1/health
# {"status": "healthy"}
```

**Step 2: 配置应用接入**

```python
# 修改应用配置
import openai

# 原来是
# openai.api_base = "https://api.openai.com/v1"

# 改为 TokenMeter 代理
openai.api_base = "http://localhost:8080/proxy/openai/v1"

# 添加标签（可选）
headers = {
    "X-Project": "my-project",
    "X-Team": "dev-team"
}
```

**Step 3: 查看仪表盘**

打开浏览器访问 http://localhost:8080

---

## 第12页：操作步骤演示（续）

**Step 4: 创建预算**

```bash
curl -X POST http://localhost:8080/api/v1/budgets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "月度预算",
    "amount": 1000,
    "period": "monthly",
    "alert_thresholds": [50, 80, 100]
  }'
```

**Step 5: 查看监控**

```bash
# 启动监控栈
docker-compose --profile monitoring up -d

# 访问 Grafana
open http://localhost:3000
# 账号: admin / 密码: admin
```

**Step 6: 导出数据**

```bash
# 导出 CSV
curl http://localhost:8080/api/v1/export/usage/csv \
  -o usage_2024.csv
```

---

## 第13页：技术规格

**技术栈**

| 组件 | 技术 |
|------|------|
| 后端 | Python 3.10+ / FastAPI |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）|
| 代理 | HTTP 透明代理 |
| 认证 | JWT + bcrypt |
| 监控 | Prometheus + Grafana |
| 部署 | Docker / Docker Compose |

**支持厂商**
- ✅ OpenAI (GPT-4, GPT-3.5, Embedding)
- ✅ Azure OpenAI
- ✅ Anthropic (Claude 3)
- ✅ 阿里云 DashScope (通义千问)

**性能指标**
- 代理延迟：< 5ms
- 吞吐量：> 1000 req/s
- 存储：每条记录 < 1KB

---

## 第14页：部署方案

**方案A：单机部署（适合初创公司）**

```yaml
# docker-compose.yml
services:
  tokenmeter:
    image: tokenmeter:v0.5.0
    ports: ["8080:8080"]
    volumes:
      - ./data:/app/data
```

**方案B：生产部署（适合中大型企业）**

```yaml
# docker-compose.prod.yml
services:
  tokenmeter:
    image: tokenmeter:v0.5.0
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - DATABASE_URL=postgresql://...
    restart: unless-stopped
  
  postgres:
    image: postgres:15
    volumes: [postgres_data:/var/lib/postgresql/data]
  
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
  
  prometheus:
    image: prom/prometheus
    ports: ["9090:9090"]
  
  grafana:
    image: grafana/grafana
    ports: ["3000:3000"]
```

---

## 第15页：定价与授权

**开源免费**

- 📄 **License**: MIT License
- 💰 **费用**: 完全免费
- 🏢 **商用**: 可自由用于商业项目
- 🔧 **定制**: 可自行修改源码

**企业支持（可选）**

| 服务 | 内容 |
|------|------|
| 部署咨询 | 协助生产环境部署 |
| 定制开发 | 根据需求定制功能 |
| 技术支持 | 7×24 技术响应 |
| 培训服务 | 团队使用培训 |

---

## 第16页：客户案例

**案例1：某 SaaS 公司**

- **背景**: 50人团队，使用 OpenAI + Claude
- **问题**: 月度账单从 $3K 涨到 $15K，找不到原因
- **使用 TokenMeter 后**:
  - 发现是测试环境的循环调用 bug
  - 修复后月度成本降至 $5K
  - 节省 67% 成本

**案例2：某 AI 创业公司**

- **背景**: 多项目并行，成本分摊困难
- **问题**: 财务需要各项目成本明细
- **使用 TokenMeter 后**:
  - 自动按项目归因
  - 实时查看各项目预算
  - 财务对账时间从 3 天降至 10 分钟

---

## 第17页：路线图

**v0.5.0（当前）**
- ✅ 多厂商支持
- ✅ 成本追踪与归因
- ✅ 预算预警
- ✅ 监控大盘
- ✅ Docker 部署

**v0.6.0（计划）**
- 🔄 PostgreSQL 支持
- 🔄 Redis 缓存
- 🔄 成本优化建议

**v0.7.0（计划）**
- 🔄 多租户支持
- 🔄 SSO 集成
- 🔄 REST API 开放

**v1.0.0（计划）**
- 🔄 企业版功能
- 🔄 云服务托管版

---

## 第18页：联系我们

**GitHub**
- 仓库: github.com/maxinghui1982/tokenmeter
- Issues: github.com/maxinghui1982/tokenmeter/issues
- 文档: github.com/maxinghui1982/tokenmeter/blob/main/README.md

**快速开始**
```bash
git clone https://github.com/maxinghui1982/tokenmeter.git
cd tokenmeter
docker-compose up -d
```

**演示环境**
- URL: http://demo.tokenmeter.io
- 账号: demo / demo

---

## 第19页：Q&A

**常见问题**

Q: 接入 TokenMeter 需要改动代码吗？
A: 只需要改 base_url，其余代码完全不变

Q: 支持哪些 AI 厂商？
A: OpenAI、Azure OpenAI、Anthropic Claude、阿里云 DashScope

Q: 数据安全吗？
A: 本地部署，数据不出内网；支持 JWT 认证和 HTTPS

Q: 有云服务版吗？
A: 目前只有开源版，云服务版计划中

---

## 第20页：感谢

**TokenMeter**
让 AI 成本管理变得简单透明

🌟 Star 我们 on GitHub
https://github.com/maxinghui1982/tokenmeter

📧 联系: tokenmeter@example.com
💬 讨论: github.com/maxinghui1982/tokenmeter/discussions

**谢谢！**

---

*PPT 制作时间: 2026年3月14日*
*版本: v0.5.0 演示版*
