---
name: Codex Task
about: A development task to be handled by Codex
title: 'T###: <Short description>'
labels: codex-task
assignees: ''
---

## Background
<!-- 业务背景：为什么要做这个，1-2 段 -->

## Success Criteria
<!-- Codex 怎么判断"做完了"？必须是机器可验证的 -->
- [ ] 文件存在：`apps/mining_pm/mining_pm/mining_pm/doctype/<name>/<name>.json`
- [ ] 文件存在：`apps/mining_pm/mining_pm/mining_pm/doctype/<name>/<name>.py`
- [ ] 文件存在：`apps/mining_pm/mining_pm/mining_pm/doctype/<name>/test_<name>.py`
- [ ] `bench --site mining.local migrate` 返回 0
- [ ] `bench --site mining.local run-tests --doctype "<Name>"` 全部通过
- [ ] `python scripts/validate-doctype.py <json path>` 返回 0
- [ ] PR 描述里关联 issue（写 `Closes #<this issue number>`）

## Field Specification
<!-- 字段清单，按这个表格填 -->

| # | fieldname | fieldtype | label | reqd | options/default | 备注 |
|---|---|---|---|---|---|---|
| 1 | naming_series | Select | 编号 | ✓ | ENG-.YYYY.-.#### | |
| 2 | ... | ... | ... | | | |

## Constraints
- Frappe v15 only
- 不引入 ERPNext
- 字段名 snake_case 英文，label 中文
- `is_submittable: 1`（如有 Draft → Submitted 流转）
- `permissions: []` 留空，由 Role Permission Manager 管

## References
- AGENTS.md（必读，运行时常驻）
- `docs/frappe-patterns/01-doctype-basics.md`（如存在）
- 兄弟 DocType（如有）作为参考
