# 乾清宫调度可视化 - working-v1 备份说明

**备份时间：** 2026-03-25 01:56
**备份文件：** `index.html.working-v1`

---

## 核心修复内容

### 1. 调度方向修复（最关键）
**问题：** 尚书令主动去找部门下达任务
**修复：** 改为部门主动到尚书令面前领任务

**原流程（错误）：**
1. 冥王→陛下领旨
2. 尚书令→冥王领旨
3. 尚书令→部门部署任务 ❌（方向反了）
4. 部门→尚书令领任务 ❌（多此一举）
5. ...

**新流程（正确）：**
1. 冥王→陛下领旨
2. 冥王回位
3. 尚书令→冥王领旨
4. 尚书令回位
5. **部门→尚书令领任务** ✅（正确方向）
6. 部门回位执行
7. 部门→尚书令汇报
8. 尚书令→冥王汇报
9. 冥王→陛下汇报
10. 冥王回位

### 2. 移动距离修复
**问题：** 小人走到一半就停了，没有到对方面前
**修复：** 将`getMidPos`的ratio从0.3改为0.8

```javascript
// 修改前
var t0 = getMidPos(mw, 'emperor', 0.3);  // 只走30%的距离

// 修改后
var t0 = getMidPos(mw, 'emperor', 0.8);  // 走80%的距离，更接近目标
```

同时修改了默认ratio：
```javascript
ratio = ratio || 0.8;  // 默认从0.5改为0.8
```

### 3. getActualLeft百分比支持
**问题：** 六部尚书令使用`left:50%`居中定位，原代码无法正确解析
**修复：** 添加百分比处理

```javascript
function getActualLeft(el) {
    var left = el.style.left;
    if (left && left.endsWith('%')) {
        return (parseFloat(left) / 100 * 1280) - 20;
    }
    return parseFloat(left || 0);
}
```

### 4. 六部尚书令加入IS_SIX_MINISTRY
```javascript
var IS_SIX_MINISTRY = {
    liubushangling:true,  // 新增
    libu:true, hubu:true, libub:true, bingbu:true, xingbu:true, gongbu:true
};
```

### 5. 一键演示按钮
- HTML中添加按钮
- `onBtnDemo()`函数处理点击
- 演示选择吏部(libu)

### 6. 六部尚书令专属调度链
当点击六部尚书令时，触发`_runLiubuShangshulingSelf`：
- 冥王→陛下领旨→回位
- 尚书令→冥王领旨→回位执行
- 尚书令→冥王汇报→回位
- 冥王→陛下汇报→回位

---

## 待完善功能（后续开发）

1. **都察院审核机制**：涉及代码开发、编写类任务需要都察院审核
2. **失败重试上报**：任务失败后重新执行并上报原因
3. **完整汇报链**：多级部门汇报时逐级上报到陛下

---

## 文件结构
```
tianqi-diting/public/qianqing/
├── index.html              # 当前工作版本
├── index.html.working-v1  # 本次备份（调度方向+移动距离修复版）
├── index.html.bak5        # 较早的稳定备份
└── ...
```
