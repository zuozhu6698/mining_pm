# Copyright (c) 2026, Mining PM and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document


class EngineeringProject(Document):
    """Engineering project master record."""

    def validate(self) -> None:
        """Ensure planned finish date is not earlier than planned start date."""
        if self.start_date and self.end_date and self.end_date < self.start_date:
            frappe.throw(_("计划竣工日期不能早于计划开工日期"))
