# 飞书文档权限转移助手

## 功能说明

批量管理飞书文档/表格/多维表格的权限，支持：
- 转移文档所有权
- 批量添加协作者（可设置查看/编辑/管理权限）
- 批量移除协作者
- 支持多种文档类型（docx/sheet/bitable/wiki）

## 适用场景

- 团队成员变动时的文档交接
- 批量设置文档权限
- 文档管理员权限调整
- 项目归档时的权限清理

## 使用方法

### 1. 转移文档所有权

```python
from feishu_perm_transfer import transfer_owner

# 转移单个文档
transfer_owner(
    doc_token="文档Token",
    doc_type="docx",  # docx/sheet/bitable/wiki
    target_open_id="接收人OpenID"
)

# 批量转移
docs = [
    {"token": "doc1", "type": "docx"},
    {"token": "doc2", "type": "sheet"},
]
for doc in docs:
    transfer_owner(doc["token"], doc["type"], "目标用户OpenID")
```

### 2. 添加协作者

```python
from feishu_perm_transfer import add_member

# 添加单个协作者
add_member(
    doc_token="文档Token",
    doc_type="docx",
    member_open_id="协作者OpenID",
    perm="edit"  # view/edit/full_access
)

# 批量添加
members = ["user1", "user2", "user3"]
for member in members:
    add_member("doc_token", "docx", member, "edit")
```

### 3. 移除协作者

```python
from feishu_perm_transfer import remove_member

# 移除单个协作者
remove_member(
    doc_token="文档Token",
    doc_type="docx",
    member_open_id="协作者OpenID"
)
```

## 权限说明

| 权限 | 说明 | 适用场景 |
|------|------|---------|
| `view` | 可查看 | 只读分享 |
| `edit` | 可编辑 | 协作编辑 |
| `full_access` | 完全访问 | 管理员 |

## 文档类型

| 类型 | 说明 |
|------|------|
| `docx` | 云文档 |
| `sheet` | 电子表格 |
| `bitable` | 多维表格 |
| `wiki` | 知识库 |

## 依赖

```bash
pip install requests
```

## ⚙️ 安装配置指南（重要！）

本 Skill 需要飞书应用权限才能正常工作，请按以下步骤配置：

### 步骤1：创建飞书应用

1. 登录 [飞书开放平台](https://open.feishu.cn)
2. 点击「创建应用」→「企业自建应用」
3. 填写应用名称（如「文档权限管理助手」）
4. 记录 **App ID** 和 **App Secret**

### 步骤2：申请权限（关键！）

进入应用详情页 →「权限管理」，申请以下权限：

| 权限 | 说明 | 是否敏感 |
|-----|------|---------|
| `drive:drive:read` | 查看云盘信息 | 否 |
| `drive:permission:write` | 管理文档权限 | ✅ 是 |
| `drive:v2:file:read` | 读取文件信息 | 否 |
| `docx:document:read` | 读取云文档 | 否 |
| `docx:document:write` | 编辑云文档 | ✅ 是 |
| `base:base:read` | 读取多维表格 | 否 |
| `base:base:write` | 编辑多维表格 | ✅ 是 |
| `contact:user:read` | 读取用户信息 | 否 |

**敏感权限说明：**
- 标记 ✅ 的权限需要管理员审批
- 在企业后台「应用审核」中查看审批状态
- 审批通常需要 1-24 小时

### 步骤3：发布应用

1. 进入「版本管理与发布」
2. 创建版本（填写版本号、更新说明）
3. 发布到「测试环境」或「线上环境」
4. 确认权限状态为「已通过」

### 步骤4：配置环境变量

**方式1：环境变量（推荐）**
```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

**方式2：代码中配置**
```python
from feishu_perm_transfer import set_credentials
set_credentials(app_id="cli_xxx", app_secret="xxx")
```

### 步骤5：验证安装

```python
from feishu_perm_transfer import get_tenant_access_token

# 测试连接
try:
    token = get_tenant_access_token()
    print("✅ 配置成功！飞书应用已就绪")
except Exception as e:
    print(f"❌ 配置失败: {e}")
    print("请检查：")
    print("  1. App ID 和 App Secret 是否正确")
    print("  2. 权限是否已审批通过")
    print("  3. 应用是否已发布")
```

---

## 🔧 常见问题

### Q1: 提示 "权限不足" 或 "99991672" 错误？
**原因：** 飞书应用没有 `drive:permission:write` 权限
**解决：** 
1. 检查权限管理页面是否已申请该权限
2. 确认管理员已审批通过
3. 重新发布应用版本

### Q2: 提示 "应用未发布"？
**原因：** 应用创建后没有发布版本
**解决：** 进入「版本管理与发布」创建并发布版本

### Q3: 如何获取文档 Token？
**方法：** 打开飞书文档 → 复制 URL → 提取 Token
```
URL: https://feishu.cn/docx/ABC123xyz
doc_token: ABC123xyz
```

### Q4: 如何获取用户 OpenID？
**方法1：** 在飞书群聊中 @用户，系统会显示 OpenID
**方法2：** 使用飞书 API 查询
```python
from feishu_perm_transfer import get_user_open_id
open_id = get_user_open_id(email="user@company.com")
```

### Q5: 批量操作被限流？
**原因：** 飞书 API 有频率限制
**解决：** 在代码中添加延迟
```python
import time
for doc in docs:
    transfer_owner(doc["token"], doc["type"], new_owner)
    time.sleep(0.5)  # 每次操作间隔0.5秒
```

## 示例：项目交接

```python
from feishu_perm_transfer import transfer_owner, add_member

# 项目文档列表
project_docs = [
    {"token": "doxcnxxx", "type": "docx", "name": "项目需求文档"},
    {"token": "shtcnxxx", "type": "sheet", "name": "项目排期表"},
    {"token": "bascnxxx", "type": "bitable", "name": "任务管理表"},
]

# 新负责人
new_owner = "ou_1eb3021737d338c63735620b218dfb08"

# 项目成员（只读权限）
members = [
    "ou_xxx1",
    "ou_xxx2",
]

print("=== 开始项目文档交接 ===")
for doc in project_docs:
    print(f"\n处理: {doc['name']}")
    
    # 1. 转移所有权
    transfer_owner(doc['token'], doc['type'], new_owner)
    print(f"  ✅ 所有权已转移给 {new_owner}")
    
    # 2. 添加项目成员（只读）
    for member in members:
        add_member(doc['token'], doc['type'], member, "view")
        print(f"  ✅ 已添加成员 {member} (view)")

print("\n=== 交接完成 ===")
```

## 注意事项

1. **权限要求**：需要飞书应用有 `drive:permission` 权限
2. **频率限制**：API有调用频率限制，批量操作建议加延迟
3. **错误处理**：建议添加try-except处理异常情况
4. **文档Token**：从飞书文档URL中获取，如 `https://feishu.cn/docx/XXX` 中的XXX

## API参考

基于飞书开放平台API：
- [权限管理API](https://open.feishu.cn/document/server-side-sdk/permission/overview)
- [云文档API](https://open.feishu.cn/document/server-side-sdk/docs/overview)

## License

MIT
