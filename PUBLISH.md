# TokenMeter 发布指南

## 项目信息

- **项目名称**: TokenMeter
- **项目描述**: 企业级 MaaS 成本追踪与归因分析平台
- **技术栈**: Python, FastAPI, SQLAlchemy, SQLite
- **开源协议**: MIT

## GitHub 发布步骤

### 1. 创建 GitHub 仓库

1. 登录 GitHub: https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - Repository name: `tokenmeter`
   - Description: `企业级 MaaS 成本追踪与归因分析平台`
   - Public/Private: 选择 Public（开源）
   - 不要勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 2. 推送本地代码

GitHub 会显示类似下面的命令，在项目目录执行：

```bash
cd /Users/apple2/.openclaw/workspace/projects/maas-cost-tracker

# 添加远程仓库（替换 yourusername 为你的 GitHub 用户名）
git remote add origin https://github.com/yourusername/tokenmeter.git

# 或者使用 SSH（需要配置 SSH 密钥）
git remote add origin git@github.com:yourusername/tokenmeter.git

# 推送代码
git branch -M main
git push -u origin main
```

### 3. 配置 GitHub 仓库

推送完成后，在 GitHub 仓库页面配置：

1. **About 部分**: 点击右侧齿轮图标
   - Website: 可选，如果有演示站点
   - Topics: `ai-cost-tracking`, `maas`, `openai`, `cost-management`, `llm-monitoring`

2. **添加 Topics 标签**:
   - artificial-intelligence
   - cost-tracking
   - llm
   - maas
   - openai
   - python
   - fastapi

### 4. 创建 Release

1. 在 GitHub 仓库页面，点击右侧 "Releases"
2. 点击 "Create a new release"
3. 选择 "Choose a tag" → 输入 "v0.1.0" → 创建新标签
4. Release title: "TokenMeter MVP"
5. 描述：复制 CHANGELOG.md 中的内容
6. 点击 "Publish release"

## 项目演示

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python -m src.main

# 3. 访问仪表盘
open http://localhost:8080

# 4. 测试代理（需要设置 OPENAI_API_KEY）
curl http://localhost:8080/proxy/openai/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 接入应用示例

```python
import openai

# 配置 TokenMeter 代理
openai.api_base = "http://localhost:8080/proxy/openai/v1"
openai.default_headers = {
    "X-Cost-Project": "my-project",
    "X-Cost-Team": "my-team"
}

# 正常调用，成本自动追踪
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## 推广建议

### 分享渠道

1. **Twitter/X**: 发推介绍项目，@相关大V
2. **V2EX**: 在「分享创造」板块发布
3. **掘金/知乎**: 写一篇项目介绍文章
4. **GitHub Trending**: 争取上热榜
5. **Hacker News**: 发布 Show HN
6. **Product Hunt**: 如果是产品化工具可发布

### 文章标题参考

- 《开源 AI 成本追踪工具：让每一分钱都花得明明白白》
- 《TokenMeter：企业级 MaaS 成本管理解决方案》
- 《告别 AI 账单黑盒：如何用 TokenMeter 追踪多源 LLM 成本》

## 后续开发计划

### v0.2.0 计划

- [ ] 支持更多 MaaS 提供商（Anthropic、Cohere、文心一言等）
- [ ] 预算预警系统（Webhook、邮件通知）
- [ ] 用户认证和权限管理
- [ ] 数据导出（CSV、Excel）

### v0.3.0 计划

- [ ] 成本优化建议引擎
- [ ] 缓存命中率分析
- [ ] Grafana/Prometheus 集成
- [ ] Docker 部署支持

### v1.0.0 计划

- [ ] 企业级功能（SSO、审计日志）
- [ ] 多租户支持
- [ ] PostgreSQL 支持
- [ ] 完善的测试覆盖

## 许可证

MIT License - 可自由用于商业和非商业项目
