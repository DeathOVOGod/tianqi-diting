# 天启帝庭 - OpenClaw 前端插件

基于 OpenClaw 的朝廷角色扮演调度系统前端。

## 功能

- 监控大屏（根路径）：系统状态可视化（Token/磁盘/内存/上下文）
- 早朝议政（/shengting）：朝廷17部门角色扮演调度系统

## 部署

### GitHub Pages（静态托管）

1. Fork 或 clone 本仓库
2. 在 GitHub Settings → Pages → Source，选择 `main` 分支和 `/ (root)` 目录
3. 访问 `https://你的用户名.github.io/tianqi-diting/`

### 本地运行

```bash
# 安装依赖
npm install

# 启动服务
node server.js

# 访问
# 监控大屏: http://localhost:18795/
# 早朝议政: http://localhost:18795/shengting
```

## 技术栈

- 前端：原生 HTML/CSS/JavaScript，Chart.js 图表库
- 后端：Node.js（静态文件服务 + WebSocket 可扩展）

## 角色系统

17个朝廷部门角色：神帝陛下、冥王帝尘、内阁、议政院、都察院、翰林院、内廷、锦衣卫、通政司、钦天监、六部尚书令、吏部、户部、礼部、兵部、刑部、工部

---

*免责声明：本项目仅供个人/小团队娱乐和研究使用，与真实政治组织无关。*
