#!/usr/bin/env python3
"""
validate-doctype.py — Frappe v15 DocType JSON 校验。

用法:
    python scripts/validate-doctype.py path/to/doctype.json

退出码: 0 = 通过，非 0 = 失败。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_TOP = {"doctype", "name", "module", "fields", "field_order"}

VALID_FIELDTYPES = {
    # 数据
    "Data", "Small Text", "Text", "Long Text", "Text Editor",
    "Markdown Editor", "Code", "HTML", "HTML Editor",
    # 数字
    "Int", "Float", "Currency", "Percent", "Rating",
    # 日期时间
    "Date", "Datetime", "Time", "Duration",
    # 选择
    "Select", "Check",
    # 关联
    "Link", "Dynamic Link", "Table", "Table MultiSelect",
    # 文件
    "Attach", "Attach Image", "Image",
    # 其他
    "Password", "JSON", "Geolocation", "Color", "Icon",
    "Barcode", "Signature", "Phone", "Autocomplete", "Read Only",
    # 布局
    "Section Break", "Column Break", "Tab Break", "Fold", "Heading",
}

LAYOUT_TYPES = {"Section Break", "Column Break", "Tab Break", "Fold", "Heading"}
PERMISSION_FLAGS = {
    "read",
    "write",
    "create",
    "delete",
    "submit",
    "cancel",
    "amend",
    "report",
    "export",
    "import",
    "share",
    "print",
    "email",
}

DEPRECATED = {"Text Chart"}
SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")
NAMING_SERIES_PAT = re.compile(
    r"^[A-Z]{2,6}-\.(YYYY|YY|MM|YYYY\.-\.MM)\.-\.####$|"
    r"^[A-Z]{2,6}-\.####$|"
    r"^[A-Z]{2,6}-\.YYYY\.-\.####$"
)

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def check(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"JSON parse error: {e}")
        return
    except FileNotFoundError:
        err(f"File not found: {path}")
        return

    # 顶层字段
    missing = REQUIRED_TOP - set(data.keys())
    if missing:
        err(f"Missing required keys: {sorted(missing)}")

    if data.get("doctype") != "DocType":
        err(f"'doctype' must be 'DocType', got {data.get('doctype')!r}")

    fields = data.get("fields", [])
    field_order = data.get("field_order", [])

    # 字段名
    fieldnames: list[str] = []
    for i, f in enumerate(fields):
        if not isinstance(f, dict):
            err(f"fields[{i}] is not a dict")
            continue

        fname = f.get("fieldname")
        ftype = f.get("fieldtype")

        is_layout = ftype in LAYOUT_TYPES

        if not is_layout:
            if not fname:
                err(f"fields[{i}] missing fieldname (fieldtype={ftype!r})")
                continue
            if fname in fieldnames:
                err(f"Duplicate fieldname: {fname!r}")
            fieldnames.append(fname)
            if not SNAKE_CASE.match(fname):
                err(f"fieldname {fname!r} not snake_case")
            if len(fname) > 8 and not re.search(r"[aeiou]", fname):
                err(f"fieldname {fname!r} suspected pinyin (no vowels)")

        # 字段类型
        if ftype not in VALID_FIELDTYPES:
            err(f"Invalid fieldtype {ftype!r} (field={fname})")
        if ftype in DEPRECATED:
            err(f"Deprecated fieldtype {ftype!r} (field={fname})")

        # Link/Table 必须有 options
        if ftype in {"Link", "Table", "Table MultiSelect", "Dynamic Link"}:
            if not f.get("options"):
                err(f"fieldtype {ftype!r} needs options (field={fname})")

    # field_order 完整性
    fields_by_name = {f.get("fieldname"): f for f in fields if f.get("fieldname")}
    for fname in field_order:
        if fname in fields_by_name:
            continue
        # Layout type 可能没 fieldname
        if not any(f.get("fieldname") == fname for f in fields):
            err(f"field_order has {fname!r} but not in fields")

    # naming_series
    naming_field = fields_by_name.get("naming_series")
    if naming_field:
        options = naming_field.get("options", "")
        for line in options.strip().splitlines():
            line = line.strip()
            if line and not NAMING_SERIES_PAT.match(line):
                err(f"naming_series option {line!r} bad format (e.g. ENG-.YYYY.-.####)")

    # permissions 可以配置；如配置，必须是 Frappe 权限行结构。
    perms = data.get("permissions", [])
    if not isinstance(perms, list):
        err("'permissions' should be a list")
    for i, perm in enumerate(perms):
        if not isinstance(perm, dict):
            err(f"permissions[{i}] is not a dict")
            continue
        if not perm.get("role"):
            err(f"permissions[{i}] missing role")
        for flag in PERMISSION_FLAGS:
            if flag in perm and perm[flag] not in {0, 1}:
                err(f"permissions[{i}].{flag} should be 0 or 1")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate-doctype.py path/to/doctype.json", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    check(path)

    if errors:
        print(f"❌ {path.name}: {len(errors)} issue(s)", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"✅ {path.name} passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
