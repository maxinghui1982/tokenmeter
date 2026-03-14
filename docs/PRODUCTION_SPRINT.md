# TokenMeter 生产就绪冲刺计划

**模式**: 马兴辉写代码，小招把控方向  
**目标**: v0.5.0 能卖给第一家客户  
**时间**: 10-15天

---

## Day 1: CI/CD 管道 (今天)

### 你的任务
创建 `.github/workflows/ci.yml`:
```yaml
# 需要包含：
# 1. Python 3.10 环境
# 2. 依赖安装
# 3. pytest 运行测试
# 4. black + flake8 代码检查
# 5. 覆盖率报告
```

### 我的把控点
- 分支保护规则（main分支需要PR+检查通过）
- 测试失败时阻止合并
- 缓存依赖加速构建

---

## Day 2-3: 测试覆盖率提升

### 你的任务
- 单元测试从29个 → 50+个
- 目标覆盖率 70%+
- 集成测试（数据库+API）

### 我的把控点
- 测试策略（哪些模块优先）
- Mock vs 真实依赖的选择
- 边界情况覆盖

---

## Day 4-5: Docker 生产优化

### 你的任务
- Dockerfile 多阶段构建
- docker-compose.prod.yml
- 健康检查配置

### 我的把控点
- 镜像大小优化
- 安全扫描
- 启动时间

---

## Day 6-7: 安全加固

### 你的任务
- JWT_SECRET 外部化
- API Key 管理（生成/撤销）
- Rate Limiting

---

## Day 8-10: 监控可观测性

### 你的任务
- Prometheus metrics
- Grafana dashboard
- 日志聚合

---

## Day 11-15: E2E测试 + 发布

### 你的任务
- 完整用户流程测试
- 性能压力测试
- CHANGELOG + 版本发布

---

**当前状态**: Day 1 进行中
