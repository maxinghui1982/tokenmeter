# TokenMeter Demo 部署指南

## 快速启动（一键脚本）

```bash
cd /Users/apple2/.openclaw/workspace/projects/maas-cost-tracker
./scripts/start-demo.sh
```

## 首次配置步骤

### 1. 安装 ngrok

```bash
# 使用 Homebrew 安装（推荐）
brew install ngrok/ngrok/ngrok

# 或者手动安装
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/ngrok.gpg && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok
```

### 2. 注册 ngrok 账号

1. 访问 https://dashboard.ngrok.com/signup
2. 使用邮箱或 GitHub 账号注册
3. 登录后获取 Authtoken

### 3. 配置 ngrok Token

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### 4. 启动 Demo

```bash
./scripts/start-demo.sh
```

你会看到类似输出：
```
🎉 Demo 环境已就绪!

   公网访问地址: https://xxxxx.ngrok-free.app
   
   本地访问地址: http://localhost:8080
```

## 手动启动（如果脚本有问题）

### 启动 TokenMeter

```bash
docker-compose up -d
```

### 启动 ngrok

```bash
ngrok http 8080
```

访问 https://dashboard.ngrok.com/cloud-edge/endpoints 查看公网地址。

## 注意事项

1. **免费版限制**：
   - 随机域名（每次重启会变）
   - 40 连接/分钟限制
   - 适合演示，不适合生产

2. **保持运行**：
   - 不要关闭终端窗口
   - 可以用 `nohup` 后台运行

3. **安全提醒**：
   - 不要在公网 Demo 上存放敏感数据
   - 演示完及时关闭

## 升级固定域名（可选）

如果需要固定域名（$5/月）：

```bash
ngrok http 8080 --domain=your-domain.ngrok.io
```

## 问题排查

### ngrok 启动失败
```bash
# 检查 token 是否配置
ngrok config check

# 查看日志
ngrok diagnose
```

### TokenMeter 启动失败
```bash
# 查看日志
docker-compose logs -f

# 重建镜像
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 端口冲突
如果 8080 被占用，修改 docker-compose.yml：
```yaml
ports:
  - "8081:8080"  # 改为 8081
```

然后：
```bash
ngrok http 8081
```
