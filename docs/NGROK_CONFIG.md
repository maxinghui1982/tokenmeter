# TokenMeter ngrok 配置

## Authtoken

```
3AtYb8UokjWL4BHmWh1vru0XpbQ_b8eCJ7aM6YFeytJf8Wvv
```

## 配置步骤

### 方法 1：自动安装（如果上面的命令还没完成）

打开新终端运行：
```bash
cd /tmp
curl -L 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.tgz' -o ngrok.tgz
tar -xzf ngrok.tgz
chmod +x ngrok
sudo mv ngrok /usr/local/bin/
rm -f ngrok.tgz

# 配置 token
ngrok config add-authtoken 3AtYb8UokjWL4BHmWh1vru0XpbQ_b8eCJ7aM6YFeytJf8Wvv
```

### 方法 2：Homebrew（推荐，如果网络允许）

```bash
brew install ngrok/ngrok/ngrok
ngrok config add-authtoken 3AtYb8UokjWL4BHmWh1vru0XpbQ_b8eCJ7aM6YFeytJf8Wvv
```

## 启动 Demo

配置完成后，启动 TokenMeter Demo：

```bash
cd /Users/apple2/.openclaw/workspace/projects/maas-cost-tracker
./scripts/start-demo.sh
```

你会看到类似输出：
```
🎉 Demo 环境已就绪!

   公网访问地址: https://xxxxx.ngrok-free.app
   本地访问地址: http://localhost:8080
```

## 测试验证

1. 访问公网地址，确认 TokenMeter 仪表盘正常
2. 测试 API 代理功能
3. 确认数据记录正常

---

**配置日期**: 2025-03-13  
**Authtoken**: 3AtYb8UokjWL4BHmWh1vru0XpbQ_b8eCJ7aM6YFeytJf8Wvv
