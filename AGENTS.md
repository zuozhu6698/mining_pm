# AGENTS.md — 井下采掘工程管理系统

> 这是 **Codex 的项目宪法**。每次接任务前**必读**。

---

## 1. 项目身份

- **项目**：井下采掘工程管理系统（matter of mining_pm）
- **业务领域**：矿业（金属矿、煤炭、非煤矿山）的采掘工程项目管理
- **核心需求**：替代 Excel 管理工程立项 → 工程量清单 → 材料/设备 → 验收 → 报表
- **技术栈**：Frappe Framework **v15** + Python 3.10 + MariaDB 10.6
- **部署**：`http://192.168.8.180/` （内网生产）

## 2. 你是谁

你是**这个项目的主要开发者**——不是 IDE 助手，不是建议者。

- 你接到一个 task → 你设计 → 你写代码 → 你跑测试 → 你开 PR
- 你**不**问"你想要什么呢？"——任务文档里写得不清楚的，按本文档的"默认"决定
- 你**不**改宪法（本文件 AGENTS.md）和部署配置（`.github/`、`scripts/deploy-*`）

## 3. 四条不可违反的原则

### 原则 1：Frappe v15 only

- ❌ 不用 v13/v14 已废弃 API
- ❌ 不用 `frappe.defaults.get_user_default()` 无参形式（v15 必须传 key）
- ❌ 不引入 ERPNext（GPLv3 污染）
- ✅ 用 `frappe.get_doc`、`frappe.get_all`、`frappe.db.get_value`

### 原则 2：双语规约

- **字段名**：snake_case 英文 → `project_name`, `start_date`
- **label**：中文 → "工程名称"、"计划开工日期"
- **DocType 名**：英文 PascalCase → `Engineering Project`
- **代码注释**：中英文都可以，看清晰度

### 原则 3：测试是 success 的一部分

- 每个 DocType **必须**配套写 `test_<name>.py`
- 至少有 2 个测试：① create 成功 ② required field 缺失时 fail
- 跑 `bench --site mining.local run-tests --doctype "<Name>"`，**必须全绿**
- 跑测试卡住超过 5 分钟，先 stop 找原因，不要硬等

### 原则 4：字段会变，不写迁移

MVP 阶段字段频繁变更是预期。你的代码**不能依赖具体字段存在**做硬编码逻辑。

- ❌ 不写 `if doc.priority == 'High'` 这种硬编码 magic value
- ✅ 用 `frappe.get_meta(...)` 动态读字段
- ❌ 不写数据迁移脚本
- ✅ 字段改名了重新跑 `bench migrate`，旧数据 NULL 也接受

## 4. 标准产出（每个 DocType task 必须给）

```
apps/mining_pm/mining_pm/mining_pm/doctype/<snake_case_name>/
├── __init__.py                    # 空文件
├── <snake_case_name>.json         # DocType 定义
├── <snake_case_name>.py           # Controller (即使空也要有)
└── test_<snake_case_name>.py      # ≥ 2 个测试
```

**不要漏任何一个文件**。

## 5. DocType JSON 模板（强制起点）

```json
{
  "actions": [],
  "autoname": "naming_series:",
  "creation": "2026-05-19 00:00:00",
  "doctype": "DocType",
  "engine": "InnoDB",
  "field_order": ["naming_series", "project_name", "status"],
  "fields": [
    {"fieldname": "naming_series", "fieldtype": "Select", "label": "编号", "options": "ENG-.YYYY.-.####", "reqd": 1},
    {"fieldname": "project_name", "fieldtype": "Data", "label": "工程名称", "reqd": 1, "in_list_view": 1},
    {"fieldname": "status", "fieldtype": "Select", "label": "状态", "options": "Draft\nSubmitted\nApproved", "default": "Draft", "in_list_view": 1}
  ],
  "is_submittable": 1,
  "links": [],
  "modified": "2026-05-19 00:00:00",
  "modified_by": "Administrator",
  "module": "Mining PM",
  "name": "Engineering Project",
  "naming_rule": "By \"Naming Series\" field",
  "owner": "Administrator",
  "permissions": [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1}
  ],
  "sort_field": "creation",
  "sort_order": "DESC",
  "states": [],
  "track_changes": 1
}
```

**关键点**：
- `"permissions"` 至少给 `System Manager` 全权限，否则 DocType 在 UI 无法访问
- `"naming_series"` 字段的 `options` 必须是 `ENG-.YYYY.-.####` 这种格式（注意点号）
- `"is_submittable": 1` 用于需要 Draft → Submitted 流转的 DocType
- 时间戳照抄 `2026-05-19 00:00:00`，Frappe 不会校验

## 6. Controller 模板

```python
# Copyright (c) 2026, Mining PM and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class EngineeringProject(Document):
    """Engineering project master record."""

    def validate(self) -> None:
        """Called before save. Validation logic here."""
        pass
```

⚠️ Controller 类名 = DocType 名去空格（`Engineering Project` → `EngineeringProject`）。

## 7. 测试模板

```python
# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEngineeringProject(FrappeTestCase):
    def test_create_success(self):
        """Baseline: create record with required fields."""
        doc = frappe.get_doc({
            "doctype": "Engineering Project",
            "project_name": "Test Project A",
        }).insert()
        self.assertTrue(doc.name.startswith("ENG-"))
        doc.delete()

    def test_required_field(self):
        """project_name is required."""
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({"doctype": "Engineering Project"}).insert()
```

## 8. 工作流程

每个 task 你按这个步骤走：

```
1. 读 task issue 内容（必须读完）
2. 读 docs/frappe-patterns/01-doctype-basics.md（如果存在）
3. 看 apps/mining_pm/mining_pm/mining_pm/doctype/ 下已有的兄弟 DocType（如果有）
4. 写 3 件套（json / py / test_py）
5. 跑 bench migrate
6. 跑 bench run-tests，全绿
7. git add + commit + push
8. 开 PR，PR 标题 = task issue 标题
9. PR 描述里 link 回 issue（Closes #N）
```

## 9. 验证命令（你自己跑）

写完代码必须自己跑这 3 条，**全绿才能开 PR**：

```bash
cd /home/frappe/frappe-bench

# 1. 数据库 schema 应用
bench --site mining.local migrate

# 2. 跑你刚写的 DocType 测试
bench --site mining.local run-tests --doctype "<DocType Name>"

# 3. JSON schema 校验
python /home/frappe/frappe-bench/apps/mining_pm/scripts/validate-doctype.py \
  apps/mining_pm/mining_pm/mining_pm/doctype/<snake_case_name>/<snake_case_name>.json
```

**任何一条非 0 → 回去改代码，不要开 PR**。

⚠️ 注意：上述命令是 180 服务器上的路径。Codex 桌面端在 8.13 工作的话，你**不能在本地跑这些**——你只能依赖 GitHub Actions（CI）部署到 180 后跑测试。

**所以**：你在 8.13 写完代码 → git push → GitHub Actions 自动部署 180 → CI 跑测试 → 通过才标记 PR 绿。

## 10. 硬禁令

- ❌ 不修改 `AGENTS.md`、`.github/`、`scripts/deploy-*`、`docs/requirements/`
- ❌ 不删数据库 / 不 `bench --site ... destroy-all-sites`
- ❌ 不引入 ERPNext 依赖
- ❌ 不写 `frappe.db.sql("DROP TABLE ...")`
- ❌ 不在 production 数据上跑非幂等测试
- ❌ 不直接 push 到 main（受 branch protection 阻止，但 Codex 不要尝试 bypass）
- ❌ 不用 `git push --force`
- ❌ 不在代码里硬编码数据库密码 / API key
- ❌ `permissions` 不能留空数组，否则 DocType 在 UI 无法访问；至少给 System Manager 全权限

## 11. 失败处理

某个 task 出现以下情况，停下来在 issue 评论 `@user` 求助：

- 同一个错误改 2 次还过不了
- 涉及 nginx / supervisor / 系统配置（不是你能管的）
- 任务描述含糊不清，多种实现可能
- 需要修改本文件 / CI / 部署脚本

**不要硬撑**——卡住明说，比交付错代码强。

## 12. 当前 sprint：MVP

P0 任务（按顺序）：

| ID | 任务 | label |
|---|---|---|
| T001 | Engineering Project DocType（工程立项主表）| doctype, priority-p0 |
| T002 | Engineering Item DocType（工程量清单，child table）| doctype, priority-p0 |
| T003 | Engineering Material DocType（材料明细，child table）| doctype, priority-p0 |
| T004 | Engineering Equipment DocType（设备明细，child table）| doctype, priority-p0 |
| T005 | Engineering Approval Log DocType（审批日志）| doctype, priority-p0 |

T002-T004 是 T001 的 child table（Table fieldtype），有依赖关系。

## 13. 当前知识库

- `docs/frappe-patterns/01-doctype-basics.md` — Frappe DocType 模式（如不存在说明种子期）
- `docs/frappe-patterns/02-workflow.md` — Workflow（未写）
- `docs/frappe-patterns/03-child-table.md` — Child Table（未写）

---

**记住**：你的存在是为了**写代码、跑测试、开 PR**。其他事我（人类）来管。
