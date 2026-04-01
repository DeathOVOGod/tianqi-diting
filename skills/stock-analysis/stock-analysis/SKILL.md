---
name: stock-analysis
description: 股票个股分析，支持多数据源自动切换，实时获取价格涨跌幅，计算技术指标和支撑位，识别缺口并判断支撑压力，智能预测未来3天走势并给出操作建议
dependency:
  python:
    - requests>=2.28.0
    - numpy>=1.24.0
    - pandas>=2.0.0
    # openclaw>=0.1.0  # 可选依赖，未安装时可使用备用数据源
  system:
    # pip install openclaw-china-market-gateway  # 可选安装

# 股票个股分析

## 任务目标
- 本 Skill 用于：对指定股票进行全面的技术分析，包括实时数据获取、技术指标计算、支撑位压力位分析、缺口识别分析
- 能力包含：实时行情获取、技术指标计算（均线、MACD、RSI）、支撑位压力位识别、缺口识别（向上/向下缺口及支撑压力作用）、趋势判断、未来走势预测
- 触发条件：用户提供股票代码并要求分析走势、预测未来、获取操作建议

## 前置准备
- 依赖说明（必需）：
  ```
  requests>=2.28.0
  numpy>=1.24.0
  pandas>=2.0.0
  ```
- 依赖说明（可选）：
  ```
  openclaw>=0.1.0  # 可选，提供更多数据源支持
  ```

## 操作步骤

### 标准流程

1. **获取股票代码并验证**
   - 用户提供股票代码，如：000001（平安银行）、sh600000（浦发银行）、000001.SZ（深交所格式）
   - 参考股票代码格式文档，确保代码格式正确

2. **获取实时行情数据（多数据源支持）**
   - 调用 `scripts/fetch_stock_data.py` 获取实时行情和历史K线数据
   - **多数据源自动切换机制**：
     - 主数据源：新浪财经（免费、稳定）
     - 备用数据源1：东方财富（免费、稳定）
     - 备用数据源2：雪球（免费、稳定）
     - 自动切换：主数据源失败时自动尝试备用数据源
   - 参数：
     - `--stock_code`: 股票代码（必需）
     - `--days`: 获取历史数据天数（默认30天）
     - `--source`: 指定数据源（可选，可选值：sina/eastmoney/xueqiu，不指定则自动切换）
   - 返回包含：当前价格、涨跌幅、成交量、历史K线数据、数据源信息

3. **计算技术指标和支撑位**
   - 调用 `scripts/analyze_stock.py` 进行技术分析
   - 参数：
     - `--data_file`: 上一步获取的数据文件路径
   - 计算结果：
     - MA5/MA10/MA20/MA60 均线
     - MACD 指标
     - RSI 指标
     - 支撑位和压力位
     - **缺口分析**（向上缺口和向下缺口）
     - 成交量分析
     - 趋势判断

4. **分析当前走势**
   - 基于技术指标进行多维度分析：
     - 均线排列（多头排列/空头排列/缠绕）
     - MACD金叉死叉状态
     - RSI超买超卖状态
     - 成交量配合情况
     - K线形态分析
     - **缺口分析**：
       - 向上缺口：通常构成支撑位（回调时缺口上沿可能成为支撑）
       - 向下缺口：通常构成压力位（反弹时缺口下沿可能成为压力）
       - 缺口大小和位置对走势的影响

5. **预测未来3天走势**
   - 综合技术指标和趋势分析，对未来3天走势进行判断
   - 考虑因素：趋势方向、支撑压力位、**缺口支撑压力**、成交量变化、市场情绪
   - 给出概率评估：上涨/下跌/横盘的概率和强度

6. **生成操作建议**
   - 根据分析结果和预测，给出明确的操作建议：
     - 买入/持有/卖出/观望
     - 建议的买入/卖出价格区间
     - 止损位和止盈位设置
     - **缺口相关的操作提示**（如：向上缺口未回补前可作为支撑参考）

## 资源索引
- 获取数据：见 [scripts/fetch_stock_data.py](scripts/fetch_stock_data.py)（用途：多数据源获取股票数据，支持自动切换）
- 技术分析：见 [scripts/analyze_stock.py](scripts/analyze_stock.py)（用途：计算技术指标和支撑位压力位）
- 代码格式：见 [references/stock_code_format.md](references/stock_code_format.md)（用途：股票代码格式参考）
- openclaw集成（可选）：见 [scripts/fetch_stock_data_openclaw.py](scripts/fetch_stock_data_openclaw.py)（用途：基于openclaw的数据获取，需安装openclaw）

## 注意事项
- 股票市场存在风险，所有分析仅供参考，不构成投资建议
- 技术分析基于历史数据，不能保证未来表现
- 建议结合基本面分析和市场环境进行综合判断
- 实时数据可能存在延迟，请以实际交易数据为准
- **数据源说明**：
  - 系统支持多数据源自动切换，提高数据获取稳定性
  - 默认使用新浪财经作为主数据源，失败时自动尝试东方财富和雪球
  - 可通过 `--source` 参数指定使用特定数据源
  - 数据源状态会在输出中明确显示
  - 如遇所有数据源均失败，请检查网络连接或稍后重试
- **openclaw 说明**（可选）：
  - openclaw 是一个开源的中国市场数据网关项目
  - 支持更多数据源（SSE/SZSE/东方财富/新浪/雪球等）
  - 目前可能未正式发布到 PyPI，建议使用已集成的备用数据源
  - 如需使用 openclaw，可从源码安装：`pip install git+https://github.com/Etherdrake/openclaw-china-market-gateway.git`
  - 未安装 openclaw 时，使用 `fetch_stock_data.py` 即可获得完整功能
- **缺口分析要点**：
  - 向上缺口（跳空高开）：通常在回调时可能构成支撑，关注缺口是否回补
  - 向下缺口（跳空低开）：通常在反弹时可能构成压力，关注缺口是否回补
  - 缺口越大，其支撑或压力作用通常越强
  - 成交量配合的缺口更具参考意义
  - 近期缺口的参考价值高于远期缺口
- 必须在所有建议中包含风险提示

## 使用示例

### 示例1：A股股票分析（推荐方式）
```
用户：分析002639雪人集团
执行：
1. 调用 fetch_stock_data.py --stock_code 002639 --days 30
2. 调用 analyze_stock.py --data_file stock_data_002639.json
3. 基于分析结果生成走势预测和操作建议
```

### 示例2：港股股票分析
```
用户：分析腾讯控股 00700.HK
执行：
1. 调用 fetch_stock_data.py --stock_code 00700.HK --days 30
2. 调用 analyze_stock.py --data_file stock_data_00700.HK.json
3. 生成分析报告和操作建议
```

### 示例3：指定数据源获取
```
用户：使用东方财富数据源分析贵州茅台
执行：
1. 调用 fetch_stock_data.py --stock_code 600519 --source eastmoney --days 30
2. 调用 analyze_stock.py --data_file stock_data_600519.json
3. 生成分析报告
```

### 示例4：美股股票分析
```
用户：分析AAPL苹果公司
执行：
1. 调用 fetch_stock_data.py --stock_code AAPL --days 30
2. 调用 analyze_stock.py --data_file stock_data_AAPL.json
3. 提供全面的技术分析报告
```

## 故障排查

### 问题：数据获取失败
**解决方案**：
1. 检查网络连接
2. 尝试指定其他数据源：`--source eastmoney` 或 `--source xueqiu`
3. 检查股票代码是否正确

### 问题：openclaw 未安装
**解决方案**：
1. 直接使用 `fetch_stock_data.py`（已实现完整功能）
2. 或尝试从源码安装 openclaw：
   ```bash
   pip install git+https://github.com/Etherdrake/openclaw-china-market-gateway.git
   ```
