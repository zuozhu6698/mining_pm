# Copyright (c) 2026, Mining PM and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class Department(Document):
    """Department master record."""

    def validate(self) -> None:
        """Prevent a department from using itself as parent."""
        if self.parent_department and self.name == self.parent_department:
            frappe.throw(_("不能引用自己作为上级"))
