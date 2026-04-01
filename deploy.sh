#!/bin/bash
#===============================================
# 天启帝庭 - 一键部署脚本
# Author: 冥王帝尘 + 昊王帝爻
# GitHub: https://github.com/DeathOVOGod/tianqi-diting
#===============================================

set -e

echo "=========================================="
echo "    天启帝庭 - 一键部署脚本"
echo "    冥王帝尘 ⚔️  昊王帝爻 ☀️"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

# 1. 检查系统环境
echo -e "${YELLOW}[1/6] 检查系统环境...${NC}"
if command -v node &> /dev/null; then
    echo "Node.js: $(node --version)"
else
    echo -e "${RED}Node.js 未安装，请先安装 Node.js 18+${NC}"
    exit 1
fi
if command -v python3 &> /dev/null; then
    echo "Python: $(python3 --version)"
else
    echo -e "${RED}Python3 未安装${NC}"
    exit 1
fi
check "系统环境检查完成"

# 2. 克隆仓库
echo ""
echo -e "${YELLOW}[2/6] 克隆天启帝庭仓库...${NC}"
if [ -d "tianqi-diting" ]; then
    echo "仓库已存在，更新中..."
    cd tianqi-diting && git pull origin main
    check "仓库更新完成"
else
    git clone https://github.com/DeathOVOGod/tianqi-diting.git
    check "仓库克隆完成"
fi

# 3. 安装依赖
echo ""
echo -e "${YELLOW}[3/6] 安装项目依赖...${NC}"
cd tianqi-diting
if [ -f "package.json" ]; then
    npm install 2>&1 | tail -5
    check "npm 依赖安装完成"
else
    echo "无 npm 依赖，跳过"
fi

# 4. 安装 Python 依赖（如果有）
if ls skills/*/requirements.txt 2>/dev/null | head -1 | grep -q .; then
    echo ""
    echo -e "${YELLOW}[4/6] 安装 Python 技能依赖...${NC}"
    for req in skills/*/requirements.txt; do
        [ -f "$req" ] && pip install -r "$req" -q 2>&1 | tail -3
    done
    check "Python 依赖安装完成"
fi

# 5. 配置 OpenClaw（可选）
echo ""
echo -e "${YELLOW}[5/6] OpenClaw 配置...${NC}"
if command -v openclaw &> /dev/null; then
    echo "OpenClaw 已安装: $(openclaw --version 2>&1 | head -1)"
    echo ""
    echo "请根据需要配置 OpenClaw："
    echo "1. 复制 skills 到 ~/.openclaw/skills/"
    echo "2. 配置飞书/Telegram 等渠道"
    echo "3. 运行: openclaw gateway start"
    check "OpenClaw 配置提示"
else
    echo -e "${YELLOW}OpenClaw 未安装（可选）${NC}"
    echo "安装命令: npm install -g openclaw"
fi

# 6. 启动天启帝庭监控大屏
echo ""
echo -e "${YELLOW}[6/6] 启动天启帝庭...${NC}"
if [ -f "server.js" ]; then
    PORT=${PORT:-18795}
    echo "启动端口: $PORT"
    echo "访问地址: http://localhost:$PORT"
    echo "按 Ctrl+C 停止"
    echo ""
    npm start &
    check "天启帝庭启动完成"
    wait
else
    echo -e "${YELLOW}无 server.js，跳过服务启动${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""
echo "项目结构："
echo "  ├── tianqi-diting/     # 天启帝庭监控大屏"
echo "  ├── skills/            # 30+ AI Agent 技能"
echo "  ├── SOUL.md            # 帝尘灵魂定义"
echo "  ├── IDENTITY.md        # 帝尘身份定义"
echo "  ├── SOUL_DiYao.md      # 帝爻灵魂定义"
echo "  ├── IDENTITY_DiYao.md  # 帝爻身份定义"
echo "  └── AGENTS.md          # 完整调度规则"
echo ""
echo "文档：https://github.com/DeathOVOGod/tianqi-diting"
echo "=========================================="
