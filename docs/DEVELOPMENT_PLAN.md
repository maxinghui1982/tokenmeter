# TokenMeter 开发测试计划

## 一、开发计划

### Sprint 规划 (敏捷开发)

#### Sprint 1: 基础加固 (2周)
**时间**: 2025年3月16日 - 3月29日  
**目标**: 提升代码质量，补充基础功能

| 任务 | 负责人 | 工时 | 优先级 |
|------|--------|------|--------|
| 完善错误处理机制 | TBD | 8h | P0 |
| 添加请求重试逻辑 | TBD | 6h | P0 |
| 实现日志系统 | TBD | 6h | P0 |
| 配置热加载 | TBD | 4h | P1 |
| Docker 支持 | TBD | 8h | P1 |
| 基础单元测试 | TBD | 12h | P0 |

**交付物**:
- [ ] 完整的错误处理和日志
- [ ] Docker 部署支持
- [ ] 60%+ 单元测试覆盖率
- [ ] 配置文件热加载

---

#### Sprint 2: 多厂商支持 (2周)
**时间**: 2025年3月30日 - 4月12日  
**目标**: 支持主流 MaaS 提供商

| 任务 | 负责人 | 工时 | 优先级 |
|------|--------|------|--------|
| Azure OpenAI 适配 | TBD | 12h | P0 |
| Anthropic Claude 适配 | TBD | 10h | P0 |
| 厂商配置管理界面 | TBD | 8h | P1 |
| 统一响应格式处理 | TBD | 6h | P1 |
| 流式响应支持 | TBD | 10h | P1 |
| 厂商健康检查 | TBD | 4h | P2 |

**交付物**:
- [ ] 支持 Azure OpenAI
- [ ] 支持 Anthropic Claude
- [ ] 流式响应代理
- [ ] 厂商管理 API

---

#### Sprint 3: 预算预警 (2周)
**时间**: 2025年4月13日 - 4月26日  
**目标**: 实现预算管理和预警系统

| 任务 | 负责人 | 工时 | 优先级 |
|------|--------|------|--------|
| 预算 CRUD API | TBD | 8h | P0 |
| 预算计算引擎 | TBD | 10h | P0 |
| Webhook 通知系统 | TBD | 8h | P0 |
| 邮件通知服务 | TBD | 6h | P1 |
| 预警历史记录 | TBD | 4h | P2 |
| 仪表盘预算展示 | TBD | 6h | P1 |

**交付物**:
- [ ] 预算设置与管理
- [ ] 多级预警触发
- [ ] 飞书/钉钉/Slack 集成
- [ ] 邮件告警

---

#### Sprint 4: 企业级功能 Phase 1 (3周)
**时间**: 2025年4月27日 - 5月17日  
**目标**: 用户认证和权限管理

| 任务 | 负责人 | 工时 | 优先级 |
|------|--------|------|--------|
| JWT 认证实现 | TBD | 10h | P0 |
| 用户管理 API | TBD | 8h | P0 |
| RBAC 权限系统 | TBD | 12h | P0 |
| LDAP 集成 | TBD | 10h | P1 |
| 审计日志 | TBD | 8h | P1 |
| API Key 管理 | TBD | 6h | P1 |

---

### 开发规范

#### 代码规范
- **语言**: Python 3.8+
- **风格**: Black + isort + flake8
- **类型**: 必须添加类型注解
- **文档**: 函数必须包含 docstring

#### Git 工作流
```
main ──→ release 分支 (生产环境)
  ↓
develop ──→ 日常开发
  ↓
feature/* ──→ 功能分支
  ↓
hotfix/* ──→ 紧急修复
```

#### 提交规范
```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具
```

---

## 二、测试计划

### 测试金字塔

```
       /\
      /  \  E2E 测试 (10%)
     /----\ 
    /      \ 集成测试 (30%)
   /--------\
  /          \ 单元测试 (60%)
 /------------\
```

### 1. 单元测试 (Unit Tests)

#### 覆盖目标
| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|----------|
| database/pricing.py | 90% | 0% |
| proxy/handler.py | 80% | 0% |
| api/routes.py | 70% | 0% |
| web/dashboard.py | 50% | 0% |

#### 测试用例设计

**pricing.py 测试用例**:
```python
# test_pricing.py
def test_calculate_cost_gpt4():
    """测试 GPT-4 成本计算"""
    cost = calculator.calculate_cost(
        provider="openai",
        model="gpt-4",
        prompt_tokens=1000,
        completion_tokens=500
    )
    assert cost["input_cost"] == 0.03  # $0.03 per 1K
    assert cost["output_cost"] == 0.03  # $0.06 per 1K * 0.5
    assert cost["total_cost"] == 0.06

def test_calculate_cost_unknown_model():
    """测试未知模型应返回 0"""
    cost = calculator.calculate_cost(
        provider="openai",
        model="unknown-model",
        prompt_tokens=1000,
        completion_tokens=500
    )
    assert cost["total_cost"] == 0.0
```

**handler.py 测试用例**:
```python
# test_handler.py
@pytest.mark.asyncio
async def test_proxy_request_success():
    """测试代理请求成功"""
    # Mock 外部 API 响应
    # 验证数据库记录创建
    # 验证响应返回
    pass

@pytest.mark.asyncio
async def test_proxy_request_with_tags():
    """测试带标签的请求正确归因"""
    # 发送带 X-Cost-* header 的请求
    # 验证数据库中 tags 正确存储
    pass
```

#### 运行命令
```bash
# 运行所有单元测试
pytest tests/unit -v --cov=src --cov-report=html

# 运行特定模块测试
pytest tests/unit/test_pricing.py -v
```

---

### 2. 集成测试 (Integration Tests)

#### 测试范围
- 数据库操作
- API 端点
- 代理转发
- 外部服务 Mock

#### 测试环境
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  tokenmeter-test:
    build: .
    environment:
      - DATABASE_URL=sqlite:///test.db
      - ENV=test
    volumes:
      - ./tests:/app/tests
```

#### 关键集成测试用例

**数据库集成**:
```python
# test_database_integration.py
def test_usage_record_crud():
    """测试使用记录的增删改查"""
    # 创建记录
    # 查询验证
    # 更新验证
    # 删除验证
    pass

def test_concurrent_writes():
    """测试并发写入"""
    # 模拟多个请求同时写入
    # 验证数据完整性
    pass
```

**API 集成**:
```python
# test_api_integration.py
def test_stats_summary_endpoint():
    """测试统计摘要 API"""
    # 插入测试数据
    # 调用 /api/v1/stats/summary
    # 验证返回数据结构
    pass

def test_proxy_openai_endpoint():
    """测试 OpenAI 代理端点"""
    # Mock OpenAI API
    # 发送请求到 /proxy/openai/v1/chat/completions
    # 验证转发和记录
    pass
```

---

### 3. E2E 测试 (End-to-End Tests)

#### 测试场景
1. 完整用户流程：配置 → 发送请求 → 查看统计
2. 预算预警流程：超预算触发 → 通知发送
3. 多厂商切换：OpenAI → Azure → Claude

#### 测试工具
- **Playwright**: Web UI 自动化
- **Postman/Newman**: API 集合测试
- **k6**: 性能测试

#### E2E 测试用例

```python
# test_e2e.py
def test_complete_user_flow():
    """
    完整用户流程测试:
    1. 启动 TokenMeter
    2. 配置 OpenAI API Key
    3. 发送 ChatCompletion 请求
    4. 验证仪表盘数据更新
    """
    pass

def test_budget_alert_flow():
    """
    预算预警测试:
    1. 设置预算 $1
    2. 发送大量请求触发超预算
    3. 验证 Webhook 通知收到
    """
    pass
```

---

### 4. 性能测试

#### 基准指标
| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| 单请求延迟增加 | < 50ms | 对比直连 vs 代理 |
| 吞吐量 | > 1000 RPS | k6 压测 |
| 内存使用 | < 500MB | 持续运行监控 |
| 数据库查询 | < 100ms | 慢查询日志 |

#### k6 性能测试脚本
```javascript
// load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  //  Ramp up
    { duration: '5m', target: 100 },  //  Steady state
    { duration: '2m', target: 200 },  //  Spike
    { duration: '2m', target: 0 },    //  Ramp down
  ],
};

export default function () {
  const payload = JSON.stringify({
    model: 'gpt-3.5-turbo',
    messages: [{ role: 'user', content: 'Hello' }],
  });

  const res = http.post('http://localhost:8080/proxy/openai/v1/chat/completions', payload, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${__ENV.OPENAI_API_KEY}`,
      'X-Cost-Project': 'load-test',
    },
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

#### 运行性能测试
```bash
# 安装 k6
brew install k6

# 运行测试（使用 Mock 服务，避免真实 API 调用）
k6 run --env OPENAI_API_KEY=test-key tests/performance/load_test.js
```

---

### 5. 安全测试

#### 安全检查清单
- [ ] API Key 不泄露到日志
- [ ] SQL 注入防护
- [ ] XSS 防护（Web 仪表盘）
- [ ] 请求频率限制（Rate Limiting）
- [ ] 敏感数据加密存储

#### 安全测试工具
```bash
# 依赖安全扫描
pip install safety
safety check

# 代码安全扫描
pip install bandit
bandit -r src/

# 容器安全扫描
docker scan tokenmeter:latest
```

---

## 三、CI/CD 流程

### GitHub Actions 工作流

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install black flake8 mypy
      - run: black --check src/
      - run: flake8 src/
      - run: mypy src/

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install bandit safety
      - run: bandit -r src/
      - run: safety check

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker build -t tokenmeter:${{ github.sha }} .
```

---

## 四、测试环境管理

### 环境矩阵

| 环境 | 用途 | 数据 | 访问控制 |
|------|------|------|----------|
| Local | 开发 | 本地 SQLite | 无 |
| Dev | 集成测试 | 测试 PostgreSQL | 团队内 |
| Staging | 预发布 | 脱敏生产数据 | 项目组 |
| Prod | 生产 | 生产 PostgreSQL | 运维团队 |

### 测试数据管理

```python
# tests/fixtures.py
@pytest.fixture
def sample_usage_records():
    """生成测试数据"""
    return [
        UsageRecord(
            request_id="req-001",
            provider="openai",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500,
            cost_total=0.06,
            project="test-project",
            team="test-team",
        ),
        # ...
    ]

@pytest.fixture
def clean_database():
    """清理测试数据库"""
    # 清理所有测试数据
    yield
    # 清理
```

---

## 五、质量门禁

### PR 合并要求
- [ ] 单元测试覆盖率 >= 70%
- [ ] 所有测试通过
- [ ] Code Review 通过（至少1人）
- [ ] Lint 检查通过
- [ ] 安全扫描无高危漏洞

### 发布检查清单
- [ ] 版本号更新
- [ ] CHANGELOG 更新
- [ ] 集成测试通过
- [ ] 性能基准达标
- [ ] 文档已更新

---

## 六、测试时间表

| 阶段 | 测试类型 | 时间 | 负责人 |
|------|----------|------|--------|
| Sprint 1 | 单元测试 | 3月16-29日 | TBD |
| Sprint 2 | 集成测试 | 3月30-4月12日 | TBD |
| Sprint 3 | E2E 测试 | 4月13-26日 | TBD |
| v0.4.0 | 性能测试 | 5月初 | TBD |
| v1.0.0 | 安全审计 | 12月 | TBD |

---

**文档版本**: 1.0  
**最后更新**: 2025-03-13  
**维护者**: TokenMeter Team
