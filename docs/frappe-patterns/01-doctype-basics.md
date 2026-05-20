# Frappe v15 DocType 模式库

> 这是项目沉淀的"Frappe 范式真相"。每次写 DocType 之前先读这个。
> 发现新坑 → 更新到这里 → 下次 AI 避开。

---

## 1. 标准 DocType JSON 模板

参考 AGENTS.md §5 的完整 JSON 模板。

## 2. 字段类型速查

| 用途 | fieldtype | 备注 |
|---|---|---|
| 短文本（≤255）| `Data` | 工程名、人名、编号 |
| 长文本 | `Long Text` | 备注、描述 |
| 富文本 | `Text Editor` | 带格式的说明 |
| 整数 | `Int` | 数量 |
| 小数 | `Float` | 进度百分比、系数 |
| 金额 | `Currency` | 预算、实际金额 |
| 日期 | `Date` | 计划日期 |
| 日期时间 | `Datetime` | 创建时间 |
| 是否 | `Check` | 0 或 1 |
| 多选枚举 | `Select` | options 用 `\n` 分隔 |
| 关联其他 DocType（单选）| `Link` | options 填目标 DocType 名 |
| 子表 | `Table` | options 填子 DocType 名 |
| 附件 | `Attach` | 单个文件 |
| 多附件 | 用 File DocType 关联 | 不要用 Attach 数组 |

## 3. naming_series 格式（强制）

```
ENG-.YYYY.-.####     ← 正确
ENG-.YY.-.####       ← 正确（短年份）
ENG-.YYYY.-.MM.-.####  ← 正确（按月）
ENG-YYYY-####        ← ❌ 错（缺点号）
ENG-.YYYY-####       ← ❌ 错（中间缺点号）
```

**点号是分隔符**。`#` 表示自增数字位数。

## 4. is_submittable

需要"草稿 → 提交 → 取消"流转的 DocType 加：

```json
"is_submittable": 1
```

加完后 DocType 自动多两个 doc.docstatus：
- 0 = Draft
- 1 = Submitted
- 2 = Cancelled

业务字段 status 和这个 docstatus 是**两件事**——业务字段是业务流转（如 Approved / Rejected），docstatus 是文档生命周期。

## 5. permissions: 必须空数组

```json
"permissions": []
```

**绝对不要在 JSON 里硬编码权限**。权限交给 Role Permission Manager 在 UI 配置。

理由：硬编码后改权限要改代码 + migrate；UI 配置随时改。

## 6. 字段命名规则

| 命名 | 评级 |
|---|---|
| `project_name` | ✅ 标准 |
| `start_date` | ✅ 标准 |
| `total_amount` | ✅ 标准 |
| `gongchengmingcheng` | ❌ 拼音 |
| `projectName` | ❌ 驼峰 |
| `Project_Name` | ❌ 首字母大写 |
| `proj` | ⚠️ 缩写不清晰 |

## 7. 字段 label 用中文

```json
{"fieldname": "project_name", "fieldtype": "Data", "label": "工程名称"}
```

label 才是用户在 UI 看到的。fieldname 是数据库列名 + 代码引用名。

## 8. Controller 何时需要

| 情况 | 是否需要逻辑 |
|---|---|
| 纯数据存储 | Controller 留空 `pass` |
| 保存前校验（如金额必须正）| `def validate(self)` |
| 提交时触发动作（生成另一个 doc）| `def on_submit(self)` |
| 删除前检查 | `def on_trash(self)` |

⚠️ 即使逻辑空，**也要创建 .py 文件**——Frappe 加载 DocType 时需要它。

## 9. 测试规约

**每个 DocType 至少 2 个测试**：

1. **test_create_success**: 用必填字段建一条记录，断言能存进数据库
2. **test_required_field**: 不传必填字段时，断言抛 `frappe.MandatoryError`

测试用 `FrappeTestCase`，自动 setUp/tearDown 数据库事务。

## 10. Child Table

Child Table 是另一个 DocType，挂在主表的 `Table` 类型字段下。

主表字段：
```json
{"fieldname": "items", "fieldtype": "Table", "label": "工程量清单", "options": "Engineering Item"}
```

Child DocType JSON 必须有：
```json
"istable": 1
```

⚠️ Child DocType **不能独立创建记录**，只能挂在主表下。

## 11. 常见错误避坑

### ❌ 错误 1：用了 v13 废弃 API

```python
# 错
frappe.defaults.get_user_default()
# 对（v15）
frappe.defaults.get_user_default("company")
```

### ❌ 错误 2：硬编码 docstatus

```python
# 错
if doc.docstatus == 1:
    # ...
# 对
if doc.docstatus == doc.STATUS_SUBMITTED:  # 或用 frappe.utils
    # ...
```

### ❌ 错误 3：用 `frappe.db.sql` 直接写 SQL

```python
# 不推荐（不可移植，绕过 ORM）
frappe.db.sql("DELETE FROM `tabEngineering Project` WHERE name='X'")
# 推荐
frappe.delete_doc("Engineering Project", "X")
```

### ❌ 错误 4：测试里 print 调试

```python
# 错
print(doc.name)
# 对
frappe.logger().info(doc.name)
```

## 12. bench 命令速查

```bash
# 数据库迁移（DocType JSON 改了之后必须跑）
bench --site mining.local migrate

# 跑测试
bench --site mining.local run-tests --doctype "Engineering Project"

# 进入 Python shell
bench --site mining.local console

# 清缓存
bench --site mining.local clear-cache

# 重建前端
bench build --app mining_pm

# 重启所有服务
sudo supervisorctl restart all
```

---

**更新本文件**：每次 Codex 踩坑被 review 出来，把那个坑记到 §11 或新章节。
