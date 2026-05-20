# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEngineeringItem(FrappeTestCase):
    def _parent(self):
        company = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": f"Test Item Company {frappe.generate_hash(length=8)}",
            }
        ).insert()
        parent = frappe.get_doc(
            {
                "doctype": "Engineering Project",
                "project_name": f"Test Item Parent {frappe.generate_hash(length=8)}",
                "company": company.name,
                "project_type": "掘进",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
            }
        ).insert()
        return parent, company

    def test_create_success(self):
        """Child row can be appended under Engineering Project."""
        parent, company = self._parent()
        parent.append(
            "items",
            {
                "item_name": "巷道开挖",
                "unit": "m³",
                "planned_quantity": 100.0,
                "unit_price": 50.0,
            },
        )
        parent.save()

        self.assertEqual(len(parent.items), 1)
        self.assertEqual(parent.items[0].total_amount, 5000.0)
        parent.delete()
        company.delete()

    def test_required_field(self):
        """item_name is required."""
        parent, company = self._parent()
        parent.append(
            "items",
            {
                "unit": "m³",
                "planned_quantity": 100.0,
            },
        )

        with self.assertRaises(frappe.MandatoryError):
            parent.save()

        parent.delete()
        company.delete()
