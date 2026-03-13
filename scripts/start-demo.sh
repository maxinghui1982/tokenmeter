#!/bin/bash
# TokenMeter Demo 一键启动脚本

echo "🚀 TokenMeter Demo 部署"
echo "======================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 ngrok
echo "📦 检查 ngrok..."
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok 未安装${NC}"
    echo "   请运行: brew install ngrok"
    exit 1
fi

# 检查 ngrok token
echo "🔑 检查 ngrok token..."
if ! ngrok config check 2>&1 | grep -q "valid"; then
    echo -e "${YELLOW}⚠️  ngrok token 未配置${NC}"
    echo ""
    echo "   请按以下步骤操作："
    echo "   1. 访问 https://dashboard.ngrok.com/signup 注册账号"
    echo "   2. 获取你的 Authtoken: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "   3. 运行: ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    echo "   获取到 token 后重新运行此脚本"
    exit 1
fi

echo -e "${GREEN}✅ ngrok 配置正确${NC}"

# 检查 Docker
echo "🐳 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")/.." || exit

# 检查 TokenMeter 是否已构建
echo "📦 检查 TokenMeter..."
if ! docker images | grep -q "tokenmeter"; then
    echo "   首次运行，需要构建镜像..."
    docker-compose build
fi

# 启动 TokenMeter
echo "🚀 启动 TokenMeter..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 检查服务状态
if curl -s http://localhost:8080/api/v1/health > /dev/null; then
    echo -e "${GREEN}✅ TokenMeter 启动成功${NC}"
else
    echo -e "${RED}❌ TokenMeter 启动失败，请检查日志: docker-compose logs${NC}"
    exit 1
fi

# 启动 ngrok
echo ""
echo "🌐 启动 ngrok 隧道..."
echo "======================="
echo ""
echo "   等待公网地址生成..."
echo ""
echo "   ${YELLOW}提示: 按 Ctrl+C 停止服务${NC}"
echo ""

# 启动 ngrok（前台运行，方便用户看到地址）
ngrok http 8080 --log=stdout | while read line; do
    echo "$line"
    # 提取并显示公网 URL
    if echo "$line" | grep -q "url=https://"; then
        URL=$(echo "$line" | grep -o "https://[a-zA-Z0-9-]*\.ngrok-free\.app")
        echo ""
        echo "=========================================="
        echo -e "${GREEN}🎉 Demo 环境已就绪!${NC}"
        echo ""
        echo -e "${GREEN}   公网访问地址: $URL${NC}"
        echo ""
        echo "   本地访问地址: http://localhost:8080"
        echo "=========================================="
        echo ""
    fi
done
