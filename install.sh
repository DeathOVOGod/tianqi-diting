#!/bin/bash
#===============================================
# 天启帝庭 - 完整一键部署脚本
# 自动安装 OpenClaw + 初始化 18 个 Agent 工作区
#===============================================

set -e

echo "=========================================="
echo "    天启帝庭 - 完整部署"
echo "    ⚔️ 冥王帝尘  ☀️ 昊王帝爻"
echo "=========================================="
echo ""

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERR]${NC} $1"; }

# 检测操作系统
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="darwin";;
    *)          PLATFORM="unknown";;
esac
log "平台: $PLATFORM"

# 1. 检查 Node.js
log "[1/8] 检查 Node.js..."
if ! command -v node &> /dev/null; then
    warn "Node.js 未安装，正在安装..."
    if [ "$PLATFORM" = "darwin" ]; then
        brew install node
    else
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs
    fi
fi
NODE_VER=$(node --version)
log "Node.js: $NODE_VER (需要 v18+)"
NPM_VER=$(npm --version)
log "npm: $NPM_VER"

# 2. 安装 OpenClaw
log "[2/8] 安装 OpenClaw..."
if command -v openclaw &> /dev/null; then
    log "OpenClaw 已安装: $(openclaw --version 2>&1 | head -1)"
else
    npm install -g openclaw 2>&1 | tail -5
    log "OpenClaw 安装完成"
fi

# 3. 创建 OpenClaw 配置目录
log "[3/8] 初始化 OpenClaw 配置..."
OPENCLAW_DIR="$HOME/.openclaw"
mkdir -p "$OPENCLAW_DIR"

# 复制配置文件模板
if [ -f "$(dirname "$0")/openclaw.json.template" ]; then
    cp "$(dirname "$0")/openclaw.json.template" "$OPENCLAW_DIR/openclaw.json"
    log "已复制 openclaw.json 配置文件"
    warn "⚠️ 请编辑 ~/.openclaw/openclaw.json 填入您的 API Key"
else
    warn "未找到 openclaw.json.template，跳过配置"
fi

# 4. 创建 Agent 工作区
log "[4/8] 创建 18 个 Agent 工作区..."

# 独立 Agent（两仪）
for agent in "workspace" "workspace-DiYao"; do
    mkdir -p "$HOME/.$agent"
    log "创建 $HOME/.$agent"
done

# 子 Agent 工作区
AGENTS=(
    "workspace-neige:内阁"
    "workspace-DiYao:昊王"
    "workspace-DiChen:冥王"
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
    "workspace-neiting:内廷"
    "workspace-jinyiwei:锦衣卫"
    "workspace-tongzhengsi:通政司"
    "workspace-shangshuling:六部尚书令"
)

for entry in "${AGENTS[@]}"; do
    dir="${entry%%:*}"
    name="${entry##*:}"
    mkdir -p "$HOME/.$dir"
    log "创建 $HOME/.$dir ($name)"
done

# 5. 复制 Agent 配置文件
log "[5/8] 部署 Agent 配置文件..."

# 复制到各自工作区
cp "$(dirname "$0")/SOUL.md" "$HOME/.workspace/SOUL.md" 2>/dev/null || true
cp "$(dirname "$0")/IDENTITY.md" "$HOME/.workspace/IDENTITY.md" 2>/dev/null || true
cp "$(dirname "$0")/AGENT.md" "$HOME/.workspace/AGENT.md" 2>/dev/null || true
cp "$(dirname "$0")/SOUL_DiYao.md" "$HOME/.workspace-DiYao/SOUL.md" 2>/dev/null || true
cp "$(dirname "$0")/IDENTITY_DiYao.md" "$HOME/.workspace-DiYao/IDENTITY.md" 2>/dev/null || true
cp "$(dirname "$0")/AGENT_DiYao.md" "$HOME/.workspace-DiYao/AGENT.md" 2>/dev/null || true
log "Agent 配置文件已部署"

# 6. 安装 Skills
log "[6/8] 安装 Skills..."

SKILLS_DIR="$HOME/.openclaw/skills"
mkdir -p "$SKILLS_DIR"

if [ -d "$(dirname "$0")/skills" ]; then
    # 复制 skills（排除可能的敏感文件）
    rsync -av --exclude='*.pyc' --exclude='__pycache__' \
        "$(dirname "$0")/skills/" "$SKILLS_DIR/" 2>/dev/null || \
        cp -r "$(dirname "$0")/skills/"* "$SKILLS_DIR/"
    log "Skills 已安装到 $SKILLS_DIR"
    log "已安装 $(ls -1 "$SKILLS_DIR" | wc -l) 个 Skills"
else
    warn "未找到 skills 目录，跳过"
fi

# 7. 部署 AGENTS.md 和 MEMORY.md
log "[7/8] 部署核心配置文件..."
for f in SOUL.md IDENTITY.md AGENT.md AGENTS.md MEMORY.md BOOTSTRAP.md TOOLS.md USER.md; do
    if [ -f "$(dirname "$0")/$f" ]; then
        cp "$(dirname "$0")/$f" "$HOME/.workspace/$f"
        log "部署 $f"
    fi
done
for f in SOUL.md IDENTITY.md AGENT.md; do
    if [ -f "$(dirname "$0")/$f" ]; then
        dest="$HOME/.workspace-DiYao/${f%.md}-DiChen${f##*.md}"
        [ "$f" = "SOUL.md" ] && dest="$HOME/.workspace-DiYao/SOUL.md"
        [ "$f" = "IDENTITY.md" ] && dest="$HOME/.workspace-DiYao/IDENTITY.md"
    fi
done

# 8. 创建便捷命令
log "[8/8] 创建便捷命令..."

# 添加到 .bashrc 或 .zshrc
SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

OPENCLAW_ALIAS='
# 天启帝庭 OpenClaw
alias openclaw-start="cd ~/.openclaw && openclaw gateway start"
alias openclaw-status="openclaw status"
alias 天启="openclaw gateway start && echo '\''天启已开，恭候陛下临朝！'\''"
alias 退朝="openclaw gateway stop && echo '\''吾皇万岁万岁万万岁'\''"
'

if ! grep -q "天启帝庭" "$SHELL_RC" 2>/dev/null; then
    echo "$OPENCLAW_ALIAS" >> "$SHELL_RC"
    log "已添加便捷命令到 $SHELL_RC"
    log "运行 source $SHELL_RC 或重启终端生效"
fi

# 验证安装
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 天启帝庭部署完成！${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 部署清单：${NC}"
echo "  ✅ OpenClaw $(openclaw --version 2>&1 | head -1)"
echo "  ✅ 18 个 Agent 工作区"
echo "  ✅ Skills $(ls -1 "$SKILLS_DIR" 2>/dev/null | wc -l) 个"
echo "  ✅ 配置文件"
echo ""
echo -e "${YELLOW}⚠️ 下一步：${NC}"
echo "  1. 编辑 ~/.openclaw/openclaw.json 填入 API Key"
echo "  2. 运行: openclaw gateway start"
echo "  3. 访问 http://localhost:18795 查看监控大屏"
echo ""
echo -e "${BLUE}📂 快捷命令：${NC}"
echo "  天启       → 启动 OpenClaw Gateway"
echo "  退朝       → 停止 OpenClaw Gateway"
echo "  openclaw-status → 查看状态"
echo ""
echo "📚 文档: https://github.com/DeathOVOGod/tianqi-diting"
echo "=========================================="
