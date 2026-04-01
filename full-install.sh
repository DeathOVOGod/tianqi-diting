#!/bin/bash
#===============================================
# 天启帝庭 - 完整一键部署脚本
# 自动安装 OpenClaw + 初始化 18 个 Agent 工作区 + 启动监控大屏
# Author: 冥王帝尘 + 昊王帝爻
# GitHub: https://github.com/DeathOVOGod/tianqi-diting
# 使用方法: bash full-install.sh
#===============================================

set -e

#===============================================
# 基础配置
#===============================================
GITHUB_REPO="https://github.com/DeathOVOGod/tianqi-diting.git"
INSTALL_DIR="$HOME/tianqi-diting"
OPENCLAW_DIR="$HOME/.openclaw"
SKILLS_DIR="$HOME/.openclaw/skills"
MONITOR_PORT="${PORT:-18795}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $1"; }
err()  { echo -e "${RED}[ERR]${NC}   $1"; }
step() { echo -e "${BLUE}[STEP]${NC}  $1"; }

#===============================================
# 欢迎横幅
#===============================================
echo ""
echo "=========================================="
echo "    天启帝庭 - 完整一键部署"
echo "    ⚔️ 冥王帝尘  ☀️ 昊王帝爻"
echo "=========================================="
echo ""

#===============================================
# Step 1: 检查系统环境
#===============================================
step "[1/9] 检查系统环境..."
if command -v node &> /dev/null; then
    log "Node.js: $(node --version)"
else
    err "Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi
if command -v npm &> /dev/null; then
    log "npm: $(npm --version)"
fi
log "系统检查完成"

#===============================================
# Step 2: 克隆仓库
#===============================================
step "[2/9] 克隆天启帝庭仓库..."
if [ -d "$INSTALL_DIR/.git" ]; then
    warn "仓库已存在，更新中..."
    cd "$INSTALL_DIR" && git pull origin main
    log "仓库更新完成"
else
    git clone "$GITHUB_REPO" "$INSTALL_DIR"
    log "仓库克隆完成"
fi

#===============================================
# Step 3: 安装 OpenClaw
#===============================================
step "[3/9] 安装 OpenClaw..."
if command -v openclaw &> /dev/null; then
    log "OpenClaw 已安装: $(openclaw --version 2>&1 | head -1)"
else
    npm install -g openclaw 2>&1 | tail -3
    log "OpenClaw 安装完成"
fi

#===============================================
# Step 4: 初始化 OpenClaw 配置
#===============================================
step "[4/9] 初始化 OpenClaw 配置..."
mkdir -p "$OPENCLAW_DIR"

if [ -f "$INSTALL_DIR/openclaw.json.template" ]; then
    if [ ! -f "$OPENCLAW_DIR/openclaw.json" ]; then
        cp "$INSTALL_DIR/openclaw.json.template" "$OPENCLAW_DIR/openclaw.json"
        log "已复制 openclaw.json 配置文件"
        warn "⚠️  请编辑 ~/.openclaw/openclaw.json 填入您的 API Key"
    else
        log "openclaw.json 已存在，跳过"
    fi
else
    warn "未找到 openclaw.json.template，跳过配置"
fi

#===============================================
# Step 5: 创建 Agent 工作区
#===============================================
step "[5/9] 创建 Agent 工作区..."

# 帝尘/帝爻主工作区
mkdir -p "$HOME/.openclaw/workspace"
mkdir -p "$HOME/.openclaw/workspace-DiYao"
log "创建 ~/.openclaw/workspace (帝尘)"
log "创建 ~/.openclaw/workspace-DiYao (帝爻)"

# 子 Agent 工作区
AGENTS=(
    "workspace-neige:内阁首辅"
    "workspace-duchayuan:都察院"
    "workspace-bingbu:兵部"
    "workspace-hubu:户部"
    "workspace-libu:礼部"
    "workspace-gongbu:工部"
    "workspace-libu2:吏部"
    "workspace-xingbu:刑部"
    "workspace-hanlinyuan:翰林院"
    "workspace-yizhengyuan:议政院"
    "workspace-qintianjian:钦天监"
    "workspace-neiting:内廷掌印"
    "workspace-jinyiwei:锦衣卫"
    "workspace-tongzhengsi:通政司"
    "workspace-shangshuling:六部尚书令"
)

for entry in "${AGENTS[@]}"; do
    dir="${entry%%:*}"
    name="${entry##*:}"
    mkdir -p "$HOME/.openclaw/$dir"
    log "创建 $dir ($name)"
done
log "共 $((${#AGENTS[@]}+2)) 个工作区"

#===============================================
# Step 6: 部署 Agent 配置文件
#===============================================
step "[6/9] 部署 Agent 配置文件..."

# 复制到帝尘工作区
for f in SOUL.md IDENTITY.md AGENT.md; do
    [ -f "$INSTALL_DIR/$f" ] && cp "$INSTALL_DIR/$f" "$HOME/.openclaw/workspace/$f"
done
log "帝尘配置文件已部署"

# 复制到帝爻工作区
for f in SOUL_DiYao.md IDENTITY_DiYao.md AGENT_DiYao.md; do
    [ -f "$INSTALL_DIR/$f" ] && cp "$INSTALL_DIR/$f" "$HOME/.openclaw/workspace-DiYao/$f"
done
log "帝爻配置文件已部署"

# 复制核心文件到帝尘工作区
for f in AGENTS.md MEMORY.md BOOTSTRAP.md TOOLS.md USER.md; do
    [ -f "$INSTALL_DIR/$f" ] && cp "$INSTALL_DIR/$f" "$HOME/.openclaw/workspace/$f"
done
log "核心配置文件已部署"

#===============================================
# Step 7: 安装 Skills
#===============================================
step "[7/9] 安装 Skills..."
mkdir -p "$SKILLS_DIR"

if [ -d "$INSTALL_DIR/skills" ]; then
    rsync -av --exclude='*.pyc' --exclude='__pycache__' \
        "$INSTALL_DIR/skills/" "$SKILLS_DIR/" 2>/dev/null || \
        cp -r "$INSTALL_DIR/skills/"* "$SKILLS_DIR/"
    SKILL_COUNT=$(ls -1 "$SKILLS_DIR" 2>/dev/null | wc -l)
    log "Skills 已安装: $SKILL_COUNT 个"
else
    warn "未找到 skills 目录，跳过"
fi

#===============================================
# Step 8: 安装 npm 依赖 + 启动监控大屏
#===============================================
step "[8/9] 安装监控大屏依赖并启动..."

if [ -f "$INSTALL_DIR/tianqi-diting/package.json" ]; then
    MONITOR_DIR="$INSTALL_DIR/tianqi-diting"
elif [ -f "$INSTALL_DIR/package.json" ]; then
    MONITOR_DIR="$INSTALL_DIR"
else
    MONITOR_DIR=""
fi

if [ -n "$MONITOR_DIR" ] && [ -f "$MONITOR_DIR/package.json" ]; then
    cd "$MONITOR_DIR"
    npm install 2>&1 | tail -3
    log "npm 依赖安装完成"

    # 杀掉旧进程
    OLD_PID=$(lsof -ti :$MONITOR_PORT 2>/dev/null || true)
    [ -n "$OLD_PID" ] && kill $OLD_PID 2>/dev/null && log "已停止旧监控进程"

    # 启动监控大屏
    cd "$MONITOR_DIR"
    PORT=$MONITOR_PORT nohup node server.js > /tmp/tianqi-monitor.log 2>&1 &
    sleep 2
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$MONITOR_PORT | grep -q "200"; then
        log "监控大屏启动成功: http://localhost:$MONITOR_PORT"
    else
        warn "监控大屏启动中，请稍后访问"
    fi
else
    warn "未找到监控大屏，跳过启动"
fi

#===============================================
# Step 9: 创建便捷命令
#===============================================
step "[9/9] 创建便捷命令..."

SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

OPENCLAW_ALIAS='
# 天启帝庭 OpenClaw
alias 天启="openclaw gateway start && echo '\''天启已开，恭候陛下临朝！'\''"
alias 退朝="openclaw gateway stop && echo '\''吾皇万岁万岁万万岁'\''"
alias 帝庭状态="openclaw status"
'

if ! grep -q "天启帝庭" "$SHELL_RC" 2>/dev/null; then
    echo "$OPENCLAW_ALIAS" >> "$SHELL_RC"
    log "已添加便捷命令到 $SHELL_RC"
fi

#===============================================
# 完成总结
#===============================================
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 天启帝庭部署完成！${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 部署清单：${NC}"
echo "  ✅ GitHub 仓库: $INSTALL_DIR"
echo "  ✅ OpenClaw $(openclaw --version 2>&1 | head -1)"
echo "  ✅ $((${#AGENTS[@]}+2)) 个 Agent 工作区"
echo "  ✅ Skills $(ls -1 "$SKILLS_DIR" 2>/dev/null | wc -l) 个"
echo "  ✅ 监控大屏 http://localhost:$MONITOR_PORT"
echo ""
echo -e "${YELLOW}⚠️  首次启动前必须：${NC}"
echo "  1. 编辑 ~/.openclaw/openclaw.json 填入您的 API Key"
echo "  2. 运行: openclaw gateway start"
echo ""
echo -e "${BLUE}📂 快捷命令：${NC}"
echo "  天启       → 启动 OpenClaw Gateway"
echo "  退朝       → 停止 OpenClaw Gateway"
echo "  帝庭状态   → 查看 OpenClaw 状态"
echo ""
echo "📚 文档: https://github.com/DeathOVOGod/tianqi-diting"
echo "=========================================="
