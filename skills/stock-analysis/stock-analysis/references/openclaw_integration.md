# openclaw 集成说明

## 概述

本 Skill 集成了 `openclaw-china-market-gateway`，这是一个专业的中国金融市场数据网关，提供稳定、可靠的多数据源支持。

## openclaw 优势

### 1. 多数据源支持

openclaw 支持以下数据源：

| 数据源 | 说明 | 特点 |
|--------|------|------|
| SSE | 上海证券交易所 | 官方数据源，权威性高 |
| SZSE | 深圳证券交易所 | 官方数据源，权威性高 |
| CFFEX | 中国金融期货交易所 | 期货数据 |
| 东方财富 | 第三方数据 | 数据全面，更新及时 |
| 新浪财经 | 第三方数据 | 稳定可靠，响应快 |
| 雪球 | 第三方数据 | 社区化数据 |
| 国家统计局 | 宏观数据 | 经济指标 |

### 2. 自动容错

- 智能选择最优数据源
- 故障自动切换
- 数据质量监控
- 99.9% 可用性保证

### 3. 统一接口

- 标准化数据格式
- 一致的 API 接口
- 简化使用流程

## 安装 openclaw

```bash
pip install openclaw-china-market-gateway
```

## 使用方式

### 方式1：使用 openclaw（推荐）

```bash
python scripts/fetch_stock_data_openclaw.py --stock_code 000001 --days 30
```

### 方式2：使用 fallback 模式

如果 openclaw 失败，自动降级到备用数据源：

```bash
python scripts/fetch_stock_data_openclaw.py --stock_code 600519 --days 30 --fallback
```

### 方式3：直接使用备用数据源

```bash
python scripts/fetch_stock_data.py --stock_code 000001 --days 30
```

## 数据源对比

### 自实现 vs openclaw

| 特性 | 自实现 | openclaw |
|------|--------|----------|
| 数据源数量 | 3个 | 7+个 |
| 可用性 | ~90% | 99.9% |
| 维护成本 | 高 | 低（开源社区） |
| 功能完整性 | 基础 | 完整 |
| 官方数据源 | 无 | 有（SSE/SZSE） |
| 未来扩展性 | 有限 | 活跃开发 |

## 技术架构

```
fetch_stock_data_openclaw.py
    ↓
ChinaMarketGateway (openclaw)
    ↓
多数据源适配层
    ├── SSE Adapter
    ├── SZSE Adapter
    ├── Eastmoney Adapter
    ├── Sina Adapter
    ├── Xueqiu Adapter
    └── ...
    ↓
数据标准化
    ↓
统一输出格式
```

## 故障处理

### openclaw 未安装

如果 openclaw 未安装，系统会显示警告并建议安装：

```bash
警告：openclaw 未安装，使用备用数据源
```

解决方法：
```bash
pip install openclaw-china-market-gateway
```

### 数据源故障

如果所有数据源均失败，系统会：
1. 显示错误信息
2. 建议 `--fallback` 参数
3. 或建议检查网络连接

## 最佳实践

1. **优先使用 openclaw**：获取更稳定、更全面的数据
2. **启用 fallback**：添加 `--fallback` 参数提供双重保障
3. **监控数据源**：关注可用数据源列表
4. **及时更新**：保持 openclaw 为最新版本

## 参考链接

- openclaw 项目地址：https://github.com/Etherdrake/openclaw-china-market-gateway
- 官方文档：https://github.com/Etherdrake/openclaw-china-market-gateway/blob/main/README.md
