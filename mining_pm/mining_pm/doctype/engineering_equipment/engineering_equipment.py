# Copyright (c) 2026, Mining PM and contributors
# For license information, please see license.txt

from __future__ import annotations

from frappe.model.document import Document
from frappe.utils import flt


class EngineeringEquipment(Document):
    """Engineering equipment row."""

    def validate(self) -> None:
        """Calculate equipment cost, preferring actual hours when present."""
        hours = flt(self.actual_hours) or flt(self.usage_hours)
        self.total_cost = hours * flt(self.hourly_rate)
