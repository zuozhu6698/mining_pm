# Copyright (c) 2026, Mining PM and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class Company(Document):
    """Company master record."""

    def validate(self) -> None:
        """Prevent a company from using itself as parent."""
        if self.parent_company and self.name == self.parent_company:
            frappe.throw(_("不能引用自己作为上级"))
