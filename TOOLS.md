# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## ⚠️ 修改前必备份规则（2026-03-25 陛下钦定）

**执行任何文件修改/写入前，必须先创建 `.bak` 备份。**

例外：MEMORY.md、HEARTBEAT.md、daily 日志等纯记录性文件无需备份。

---

## 调度原则
- 用 sessions_spawn 并行调度多个 agent
- agentId: neige(内阁)、neiting(内廷)、liubusima(六部司马)、yizhengyuan(议政院)、duchayuan(都察院)、hanlinyuan(翰林院)、jinyiwei(锦衣卫)、tongzhengsi(通政司)、qintianjian(钦天监)、bingbu(兵部)、hubu(户部)、libu(礼部)、gongbu(工部)、libu2(吏部)、xingbu(刑部)
- 内阁(neige)调度：议政院、都察院、翰林院（三院）
- 内廷(neiting)调度：锦衣卫、通政司、钦天监（三机构）
- 六部(liubusima)调度：兵部、户部、礼部、工部、吏部、刑部（六部）
- 完成后主动汇报，不让陛下等
- 完成后主动汇报，不让陛下等

## 飞书文档命令（最高优先级）
- **禁止**：私自创建文档
- **必须**：严格在陛下指定的文档中写入/更新
- 每次写入前必须确认文档 ID 和位置


## 虾评Skill（技能市场）
- 平台：https://xiaping.coze.site
- API Key：sk_5jnHWQf0ygKlfRhMRkinMrggJKurIs12
- 已安装11个技能（见MEMORY.md）

## 技能触发词
- /news-aggregator-skill — 全网新闻聚合
- /humanizer-zh — AI文本去味
- /coze-web-search — 网页搜索
- /feishu-doc-writer — 飞书文档
- /feishu-bitable — 飞书多维表格
- /lidan-writing — 七步写作
- /cold-email — 文案写作
- /cover-image — 封面生成
- /stock-analysis — 股票分析
- /feishu-perm-assist — 飞书文档权限转移
- /ui-ux-design — UI/UX设计专家
