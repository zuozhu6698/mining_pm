"""
Reload all fixtures declared in hooks.py on every migrate.

Why: Frappe's default fixture loading is not idempotent. Once fixtures are loaded
during install-app, subsequent edits to fixture JSON files have no effect on the
database. This patch forces re-import so AI-driven fixture changes actually
reach production.

Idempotency: safe to run multiple times. Each fixture entry's name is the
primary key, and Frappe upserts on import.
"""
from __future__ import annotations

from pathlib import Path

import frappe
from frappe.modules.import_file import import_file_by_path


def execute() -> None:
    """Re-import all mining_pm fixture files."""
    app_path = frappe.get_app_path("mining_pm")
    fixtures_dir = Path(app_path) / "mining_pm" / "fixtures"

    if not fixtures_dir.exists():
        print(f"[sync_fixtures] No fixtures dir at {fixtures_dir}, skip")
        return

    json_files = sorted(fixtures_dir.glob("*.json"))
    if not json_files:
        print(f"[sync_fixtures] No JSON files in {fixtures_dir}, skip")
        return

    for json_file in json_files:
        print(f"[sync_fixtures] Importing {json_file.name}...")
        try:
            import_file_by_path(
                str(json_file),
                force=True,
                ignore_version=True,
                reset_permissions=False,
            )
            print(f"[sync_fixtures]   OK {json_file.name} imported")
        except Exception as exc:
            print(f"[sync_fixtures]   WARN {json_file.name} failed: {exc}")

    frappe.db.commit()
    frappe.clear_cache()
    print("[sync_fixtures] Done")
