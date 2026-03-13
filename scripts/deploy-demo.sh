#!/bin/bash
# TokenMeter Demo 部署脚本
# 使用 ngrok 内网穿透

echo "🚀 TokenMeter Demo 部署脚本"
echo "=============================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 启动 TokenMeter
echo "📦 启动 TokenMeter..."
docker-compose up -d

# 检查是否已安装 ngrok
if ! command -v ngrok &> /dev/null; then
    echo "📥 安装 ngrok..."
    
    # 检测系统架构
    if [[ $(uname -m) == "arm64" ]]; then
        NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-arm64.zip"
    else
        NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip"
    fi
    
    curl -L $NGROK_URL -o ngrok.zip
    unzip ngrok.zip
    sudo mv ngrok /usr/local/bin/
    rm ngrok.zip
    
    echo "⚠️  请访问 https://dashboard.ngrok.com/get-started/your-authtoken 获取 token"
    echo "   然后运行: ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

# 启动 ngrok
echo "🌐 启动 ngrok 隧道..."
echo "   公网地址将显示在下方:"
echo "=============================="
ngrok http 8080
