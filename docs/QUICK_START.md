# TokenMeter 快速试用指南

**版本**: v0.5.0  
**预计时间**: 10 分钟  
**难度**: ⭐⭐ 简单

---

## 📋 试用前准备

### 系统要求
- Docker 20.10+ 和 Docker Compose 2.0+
- 4GB 可用内存
- 10GB 磁盘空间

### 准备工具
- 终端/命令行工具
- 浏览器（Chrome/Firefox/Safari）
- 文本编辑器（VSCode/Sublime/Vim）

### API Key（可选）
- OpenAI API Key（用于测试代理功能）

---

## 🚀 5分钟快速启动

### Step 1: 克隆仓库（1分钟）

```bash
# 克隆代码
git clone https://github.com/maxinghui1982/tokenmeter.git

# 进入目录
cd tokenmeter
```

**预期输出**:
```
Cloning into 'tokenmeter'...
remote: Enumerating objects: 1234, done.
Receiving objects: 100% (1234/1234), done.
```

---

### Step 2: 启动服务（2分钟）

```bash
# 启动 TokenMeter
docker-compose up -d
```

**预期输出**:
```
[+] Running 3/3
 ✔ Network tokenmeter_default  Created
 ✔ Container tokenmeter-app    Started
 ✔ Container tokenmeter-db     Started
```

**检查状态**:
```bash
curl http://localhost:8080/api/v1/health
```

**预期输出**:
```json
{"status": "healthy", "version": "0.5.0"}
```

✅ **成功！** TokenMeter 已启动

---

### Step 3: 访问仪表盘（1分钟）

打开浏览器访问: http://localhost:8080

**界面说明**:
- 📊 **概览数据**: 总请求数、总成本、活跃项目
- 📈 **成本趋势**: 最近30天成本走势
- 📋 **调用记录**: 详细的 API 调用日志

**截图示意**:
```
┌────────────────────────────────────────────────────┐
│  TokenMeter v0.5.0                                 │
├────────────────────────────────────────────────────┤
│                                                    │
│  📊 概览数据                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ 总请求数 │  │  总成本  │  │ 活跃项目 │         │
│  │    0     │  │ $0.00   │  │    0     │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│                                                    │
│  [开始使用] 按钮                                   │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 🧪 功能试用

### 试用 1: 测试代理功能（3分钟）

**准备测试脚本**:

创建一个 `test_proxy.py` 文件:

```python
import openai

# 配置 TokenMeter 代理
openai.api_base = "http://localhost:8080/proxy/openai/v1"
openai.api_key = "sk-your-openai-api-key"

# 添加标签（可选）
headers = {
    "X-Project": "demo-project",
    "X-Team": "demo-team",
    "X-Environment": "testing"
}

# 发送请求
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello, TokenMeter!"}
        ],
        headers=headers
    )
    print("✅ 请求成功！")
    print(f"回复: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ 请求失败: {e}")
```

**运行测试**:

```bash
# 安装依赖
pip install openai

# 运行测试
python test_proxy.py
```

**预期输出**:
```
✅ 请求成功！
回复: Hello! How can I help you today?
```

**验证记录**:
1. 刷新浏览器 http://localhost:8080
2. 查看 "最近调用记录"
3. 确认看到刚才的调用记录

✅ **代理功能正常！**

---

### 试用 2: 创建预算（2分钟）

**步骤**:

1. 点击左侧菜单 "预算管理"
2. 点击 "创建预算" 按钮
3. 填写表单:
   - 预算名称: `试用预算`
   - 预算金额: `100`
   - 周期: `monthly`
   - 告警阈值: `50, 80, 100`
4. 点击保存

**验证**:
- 预算列表中显示刚创建的预算
- 使用率为 0%（还没有产生成本）

---

### 试用 3: 查看统计（1分钟）

**步骤**:

1. 点击左侧菜单 "统计分析"
2. 查看以下维度:
   - 按提供商统计
   - 按项目统计
   - 按团队统计

**预期**:
- 显示 OpenAI 的调用数据
- 显示 `demo-project` 的项目数据
- 显示 `demo-team` 的团队数据

---

## 📊 启动监控（可选，2分钟）

如果你想试用 Prometheus + Grafana 监控:

```bash
# 启动监控栈
docker-compose --profile monitoring up -d
```

**访问地址**:
- Grafana: http://localhost:3000
  - 账号: `admin`
  - 密码: `admin`
- Prometheus: http://localhost:9090

**查看指标**:
1. 登录 Grafana
2. 点击左侧 "Dashboards"
3. 选择 "TokenMeter Dashboard"
4. 查看实时指标

---

## 🔧 常见问题

### Q1: Docker 启动失败

**现象**: `docker-compose up -d` 报错

**解决**:
```bash
# 检查 Docker 状态
docker ps

# 如果端口被占用，修改 docker-compose.yml 中的端口
# 将 "8080:8080" 改为 "8081:8080"
```

---

### Q2: 代理请求失败

**现象**: `test_proxy.py` 报错 Connection refused

**解决**:
```bash
# 检查服务状态
docker-compose ps

# 如果状态不是 Up，查看日志
docker-compose logs tokenmeter

# 重启服务
docker-compose restart
```

---

### Q3: 仪表盘显示空白

**现象**: 浏览器打开 http://localhost:8080 空白

**解决**:
```bash
# 等待几秒钟，服务可能还在启动中
# 检查健康状态
curl http://localhost:8080/api/v1/health

# 如果返回 healthy，刷新浏览器
# 如果仍有问题，清除浏览器缓存
```

---

### Q4: API Key 无效

**现象**: 返回 401 Unauthorized

**解决**:
- 确认 OpenAI API Key 有效
- 检查 API Key 是否已过期
- 确认有足够的额度

---

## 🎯 试用清单

| 功能 | 是否试用 | 结果 |
|------|----------|------|
| ✅ 服务启动 | ☐ | |
| ✅ 仪表盘访问 | ☐ | |
| ✅ 代理功能 | ☐ | |
| ✅ 成本记录 | ☐ | |
| ✅ 预算创建 | ☐ | |
| ✅ 统计分析 | ☐ | |
| ✅ 监控大盘 | ☐ | |

---

## 📝 反馈收集

试用后请提供反馈:

1. **部署是否顺利**: ⭐⭐⭐⭐⭐
2. **文档是否清晰**: ⭐⭐⭐⭐⭐
3. **功能是否符合预期**: ⭐⭐⭐⭐⭐
4. **遇到的问题**: ___________
5. **改进建议**: ___________

**反馈方式**:
- GitHub Issues: https://github.com/maxinghui1982/tokenmeter/issues
- 飞书群讨论

---

## 🚀 下一步

试用满意后，可以:

1. **生产部署**: 参考 `docker-compose.prod.yml`
2. **数据导出**: 使用 `/api/v1/export/usage/csv` 接口
3. **预算告警**: 配置飞书 Webhook
4. **自定义开发**: Fork 仓库，按需修改

---

## 📚 更多文档

- [完整文档](https://github.com/maxinghui1982/tokenmeter/blob/main/README.md)
- [API 文档](https://github.com/maxinghui1982/tokenmeter/blob/main/docs/API.md)
- [部署指南](https://github.com/maxinghui1982/tokenmeter/blob/main/docs/DEPLOYMENT.md)

---

**试用时间**: 约 10 分钟  
**遇到问题?** 查看 [FAQ](#常见问题) 或提交 Issue

**祝你试用愉快！** 🎉
