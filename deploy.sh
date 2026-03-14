#!/bin/bash
# TokenMeter 生产环境部署脚本
# Usage: ./deploy.sh [production|development]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 环境选择
ENV=${1:-production}
COMPOSE_FILE="docker-compose.prod.yml"

if [ "$ENV" = "development" ]; then
    COMPOSE_FILE="docker-compose.yml"
    echo -e "${YELLOW}使用开发环境配置...${NC}"
else
    echo -e "${GREEN}使用生产环境配置...${NC}"
fi

# 检查 Docker
echo -e "${YELLOW}检查 Docker 环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

# 创建必要目录
echo -e "${YELLOW}创建数据目录...${NC}"
mkdir -p data logs nginx/ssl

# 检查 JWT_SECRET
if [ -z "$JWT_SECRET" ] && [ "$ENV" = "production" ]; then
    echo -e "${YELLOW}警告: JWT_SECRET 环境变量未设置${NC}"
    echo -e "${YELLOW}生成随机 JWT_SECRET...${NC}"
    export JWT_SECRET=$(openssl rand -hex 32)
    echo -e "${GREEN}JWT_SECRET 已生成，请保存: $JWT_SECRET${NC}"
fi

# 构建镜像
echo -e "${YELLOW}构建 Docker 镜像...${NC}"
docker-compose -f $COMPOSE_FILE build

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker-compose -f $COMPOSE_FILE up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 5

# 健康检查
echo -e "${YELLOW}执行健康检查...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8080/api/v1/health | grep -q "healthy"; then
        echo -e "${GREEN}✓ TokenMeter 启动成功!${NC}"
        echo -e "${GREEN}  访问地址: http://localhost:8080${NC}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}  等待服务就绪... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 3
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ 服务启动失败，请检查日志:${NC}"
    echo -e "${RED}  docker-compose -f $COMPOSE_FILE logs${NC}"
    exit 1
fi

# 显示状态
echo -e "${GREEN}=== 部署完成 ===${NC}"
docker-compose -f $COMPOSE_FILE ps

echo ""
echo -e "${GREEN}常用命令:${NC}"
echo "  查看日志: docker-compose -f $COMPOSE_FILE logs -f"
echo "  停止服务: docker-compose -f $COMPOSE_FILE down"
echo "  重启服务: docker-compose -f $COMPOSE_FILE restart"
