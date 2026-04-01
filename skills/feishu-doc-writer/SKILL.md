# 飞书云文档写作助手

## 功能说明

一站式飞书云文档创作工具，支持：
- 创建飞书云文档（docx）
- 写入/追加文档内容
- Markdown格式自动转换
- 丰富的文档模板
- 批量文档生成

## 适用场景

- 快速创建会议纪要
- 自动生成周报/月报
- 项目文档标准化
- 批量生成报告
- 知识库建设

## 使用方法

### 1. 创建文档

```python
from feishu_doc_writer import DocWriter

writer = DocWriter()

# 创建空白文档
doc_token = writer.create_doc("项目名称 - 会议纪要")
print(f"文档已创建: https://feishu.cn/docx/{doc_token}")

# 使用模板创建
doc_token = writer.create_doc_from_template(
    title="周报 - 第10周",
    template="weekly_report"
)
```

### 2. 写入内容

```python
# 写入文本内容
writer.write_content(
    doc_token=doc_token,
    content="""# 会议纪要

## 参会人员
- 张三
- 李四

## 会议内容
1. 项目进度同步
2. 下阶段计划
"""
)

# 追加内容
writer.append_content(
    doc_token=doc_token,
    content="\n## 行动项\n- [ ] 完成任务A\n- [ ] 完成任务B"
)
```

### 3. Markdown转飞书文档

```python
# Markdown自动转换
markdown_text = """
# 项目提案

## 背景
项目背景描述...

## 目标
- 目标1
- 目标2

## 时间规划
| 阶段 | 时间 | 任务 |
|------|------|------|
| 阶段1 | 第1周 | 需求分析 |
| 阶段2 | 第2-3周 | 开发实现 |
"""

writer.write_markdown(doc_token, markdown_text)
```

### 4. 使用模板

```python
# 会议纪要模板
data = {
    "title": "产品评审会议",
    "date": "2024-03-09",
    "attendees": ["产品经理", "设计师", "开发负责人"],
    "topics": ["需求确认", "UI评审", "排期讨论"],
    "decisions": ["确定V1.0功能范围", "UI风格采用方案A"],
    "actions": [
        {"task": "输出PRD", "owner": "产品经理", "deadline": "3月12日"},
        {"task": "设计稿终稿", "owner": "设计师", "deadline": "3月15日"}
    ]
}

doc_token = writer.create_from_template("meeting_minutes", data)

# 周报模板
data = {
    "week": "第10周",
    "date_range": "3/4 - 3/8",
    "completed": ["完成需求评审", "完成技术方案"],
    "in_progress": ["接口开发", "单元测试"],
    "next_week": ["联调测试", "文档编写"],
    "issues": ["第三方接口延迟"]
}

doc_token = writer.create_from_template("weekly_report", data)
```

## 内置模板

| 模板名称 | 说明 | 适用场景 |
|---------|------|---------|
| `meeting_minutes` | 会议纪要 | 会议记录 |
| `weekly_report` | 周报 | 每周工作总结 |
| `monthly_report` | 月报 | 月度工作汇报 |
| `project_proposal` | 项目提案 | 项目立项 |
| `product_requirement` | 产品需求文档 | PRD编写 |
| `technical_design` | 技术方案 | 技术评审 |

## 文档格式支持

### 支持的Markdown语法

- 标题 `# ## ###`
- 列表 `-` `1.`
- 加粗 `**文本**`
- 斜体 `*文本*`
- 链接 `[文本](url)`
- 表格 `| 列1 | 列2 |`
- 代码块 ` ```代码``` `
- 分割线 `---`

### 飞书特有格式

```python
# 添加@提及
writer.add_mention(doc_token, "ou_xxx", "张三")

# 添加评论
writer.add_comment(doc_token, "需要补充细节")

# 添加图片（需要先上传）
writer.add_image(doc_token, image_token)
```

## 批量生成

```python
# 批量生成周报
weeks = ["第8周", "第9周", "第10周"]
for week in weeks:
    data = {
        "week": week,
        "completed": ["任务A", "任务B"],
        "next_week": ["任务C"]
    }
    doc_token = writer.create_from_template("weekly_report", data)
    print(f"{week}周报已生成: {doc_token}")

# 批量创建会议纪要
meetings = [
    {"title": "需求评审", "date": "3/1"},
    {"title": "技术评审", "date": "3/5"},
    {"title": "项目复盘", "date": "3/8"},
]

for meeting in meetings:
    data = {
        "title": meeting["title"],
        "date": meeting["date"],
        "attendees": ["参会人员"],
        "topics": ["讨论内容"]
    }
    doc_token = writer.create_from_template("meeting_minutes", data)
```

## 高级用法

### 文档结构化写入

```python
from feishu_doc_writer.blocks import *

# 使用Block构建文档
blocks = [
    Heading1("项目总结"),
    Text("项目圆满结束，以下是总结："),
    
    Heading2("成果展示"),
    BulletedList(["功能A上线", "用户增长50%", "性能提升30%"]),
    
    Heading2("数据对比"),
    Table(
        headers=["指标", "Before", "After"],
        rows=[
            ["用户数", "1000", "1500"],
            ["留存率", "30%", "45%"]
        ]
    ),
    
    Divider(),
    
    Callout("info", "感谢团队的努力！")
]

writer.write_blocks(doc_token, blocks)
```

### 文档协作

```python
# 创建文档并设置权限
doc_token = writer.create_doc("协作文档")

# 添加协作者
writer.add_collaborator(doc_token, "ou_xxx", perm="edit")

# 添加评论
writer.add_comment(doc_token, "请大家补充内容")
```

## 依赖

```bash
pip install requests
```

## 配置

```python
import os
os.environ["FEISHU_APP_ID"] = "cli_xxx"
os.environ["FEISHU_APP_SECRET"] = "xxx"
```

## 注意事项

1. **权限要求**：需要 `docx:document:write` 权限
2. **格式限制**：Markdown转飞书格式可能有部分差异
3. **图片上传**：大图片需要先上传到飞书云盘
4. **频率限制**：批量操作建议加延迟

## 示例：完整工作流

```python
from feishu_doc_writer import DocWriter

# 初始化
writer = DocWriter()

# 1. 创建会议纪要
doc_token = writer.create_doc("产品评审会议 - 2024.03.09")

# 2. 写入内容（Markdown格式）
content = """
# 产品评审会议

## 基本信息
- **时间**: 2024-03-09 14:00-15:30
- **地点**: 会议室A
- **主持人**: 产品经理

## 参会人员
1. 产品经理
2. UI设计师
3. 前端负责人
4. 后端负责人

## 议程
1. 需求背景介绍 (15min)
2. 方案讨论 (45min)
3. 排期确认 (15min)
4. 风险评估 (15min)

## 会议结论
- ✅ 确定V1.0功能范围
- ✅ UI风格采用方案A
- ⚠️ 技术难点需要进一步调研

## 行动项
| 任务 | 负责人 | 截止日期 |
|------|--------|----------|
| 输出PRD文档 | 产品经理 | 3月12日 |
| 设计稿终稿 | UI设计师 | 3月15日 |
| 技术方案评审 | 技术负责人 | 3月13日 |

## 附件
- [需求文档](#)
- [设计稿](#)
"""

writer.write_markdown(doc_token, content)

# 3. 添加评论
writer.add_comment(doc_token, "@所有人 请确认行动项")

print(f"✅ 会议纪要已生成: https://feishu.cn/docx/{doc_token}")
```

## API参考

- [飞书云文档API](https://open.feishu.cn/document/server-side-sdk/docs/overview)
- [文档块API](https://open.feishu.cn/document/server-side-sdk/docs/block)

## License

MIT
