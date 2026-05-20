# T001: Engineering Project DocType

## Background

井下采掘工程管理系统的主表。一个 Engineering Project = 一次采掘工程立项。
后续的工程量清单、材料、设备、审批都挂在它下面。

这是 MVP 阶段的第一个 DocType，其他 4 个 child table（Item / Material / Equipment / ApprovalLog）依赖它先存在。

## Success Criteria

- [ ] 文件存在：`apps/mining_pm/mining_pm/mining_pm/doctype/engineering_project/engineering_project.json`
- [ ] 文件存在：`apps/mining_pm/mining_pm/mining_pm/doctype/engineering_project/engineering_project.py`
- [ ] 文件存在：`apps/mining_pm/mining_pm/mining_pm/doctype/engineering_project/test_engineering_project.py`
- [ ] 文件存在：`apps/mining_pm/mining_pm/mining_pm/doctype/engineering_project/__init__.py`（空）
- [ ] `bench --site mining.local migrate` 返回 0
- [ ] `bench --site mining.local run-tests --doctype "Engineering Project"` 全部通过
- [ ] `python scripts/validate-doctype.py apps/mining_pm/mining_pm/mining_pm/doctype/engineering_project/engineering_project.json` 返回 0

⚠️ Codex 在 8.13 本地写代码无法跑 bench 验证。本地只能跑：
- `python scripts/validate-doctype.py ...`（这条本地能跑）

bench migrate 和 run-tests 由 CI 在 180 上跑，PR 自动触发。

## Field Specification（17 个字段，本期暂不含 child table 字段）

| # | fieldname | fieldtype | label | reqd | options/default | 备注 |
|---|---|---|---|---|---|---|
| 1 | naming_series | Select | 编号 | ✓ | `ENG-.YYYY.-.####` | |
| 2 | project_name | Data | 工程名称 | ✓ | | in_list_view=1 |
| 3 | project_code | Data | 工程编码 | | | 可手工覆盖 |
| 4 | company | Link | 所属公司 | ✓ | options: `Company` | |
| 5 | department | Link | 施工部门 | | options: `Department` | |
| 6 | project_type | Select | 工程类型 | ✓ | `掘进\n采矿\n支护\n运输\n其他` | |
| 7 | mine_area | Data | 矿区 | | | |
| 8 | tunnel_level | Data | 中段/标高 | | | |
| 9 | start_date | Date | 计划开工日期 | ✓ | | |
| 10 | end_date | Date | 计划竣工日期 | ✓ | | |
| 11 | actual_start_date | Date | 实际开工日期 | | | |
| 12 | actual_end_date | Date | 实际竣工日期 | | | |
| 13 | designer | Link | 设计人 | | options: `User` | |
| 14 | approver | Link | 审批人 | | options: `User` | |
| 15 | status | Select | 状态 | ✓ | `Draft\nSubmitted\nApproved\nIn Progress\nCompleted\nRejected` 默认 `Draft` | in_list_view=1 |
| 16 | total_budget | Currency | 预算金额 | | | |
| 17 | notes | Text Editor | 备注说明 | | | |

字段顺序建议加 2 个布局元素：
- 在字段 9 前加 `Section Break` (label: "时间安排")
- 在字段 13 前加 `Section Break` (label: "人员")
- 在字段 16 前加 `Section Break` (label: "财务")

## DocType 顶层属性

```json
{
  "doctype": "DocType",
  "name": "Engineering Project",
  "module": "Mining PM",
  "engine": "InnoDB",
  "autoname": "naming_series:",
  "naming_rule": "By \"Naming Series\" field",
  "is_submittable": 1,
  "track_changes": 1,
  "sort_field": "creation",
  "sort_order": "DESC",
  "permissions": []
}
```

## Controller 要求

```python
from frappe.model.document import Document


class EngineeringProject(Document):
    def validate(self) -> None:
        """计划日期校验：end_date 必须 >= start_date"""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            import frappe
            frappe.throw("计划竣工日期不能早于计划开工日期")
```

## 测试要求（≥ 3 个）

1. **test_create_success**: 用最少必填字段创建一条记录，断言 `name` 以 `ENG-` 开头
2. **test_required_field**: 不传 `project_name` 时抛 `MandatoryError`
3. **test_date_validation**: `end_date < start_date` 时抛错（验证 Controller 的 validate）

## Constraints

- Frappe v15
- 不引入 ERPNext（Company / Department / User 都是 Frappe 自带的，不算 ERPNext）
- 字段名 snake_case 英文，label 中文
- `permissions: []` 留空

## References

- [AGENTS.md](AGENTS.md)
- [docs/frappe-patterns/01-doctype-basics.md](docs/frappe-patterns/01-doctype-basics.md)
