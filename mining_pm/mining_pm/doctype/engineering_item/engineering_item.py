# Copyright (c) 2026, Mining PM and contributors
# For license information, please see license.txt

from __future__ import annotations

from frappe.model.document import Document
from frappe.utils import flt


class EngineeringItem(Document):
    """Engineering quantity item row."""

    def validate(self) -> None:
        """Calculate planned amount from planned quantity and unit price."""
        self.total_amount = flt(self.planned_quantity) * flt(self.unit_price)
