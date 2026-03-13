# TokenMeter 贡献指南

感谢你对 TokenMeter 项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请通过 GitHub Issues 报告，并包含以下信息：

- 问题的清晰描述
- 复现步骤
- 期望行为 vs 实际行为
- 运行环境（OS、Python 版本等）
- 相关日志或错误信息

### 提交功能请求

如果你有新功能的想法，欢迎提交 Feature Request：

- 描述你想要的功能
- 说明使用场景
- 如果可能，提供实现思路

### 提交代码

1. Fork 本项目
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 为新功能添加测试
- 更新相关文档
- 确保所有测试通过

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/tokenmeter.git
cd tokenmeter

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest
```

## 联系方式

如有任何问题，欢迎：

- 在 GitHub Discussions 中提问
- 发送邮件至: your-email@example.com

再次感谢你的贡献！