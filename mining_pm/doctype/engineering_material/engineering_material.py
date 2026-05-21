# Copyright (c) 2026, Mining PM and contributors
# For license information, please see license.txt

from __future__ import annotations

from frappe.model.document import Document
from frappe.utils import flt


class EngineeringMaterial(Document):
    """Engineering material row."""

    def validate(self) -> None:
        """Calculate material cost, preferring actual quantity when present."""
        quantity = flt(self.actual_qty) or flt(self.planned_qty)
        self.total_cost = quantity * flt(self.unit_price)
