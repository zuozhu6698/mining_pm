# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEngineeringEquipment(FrappeTestCase):
    def _parent(self):
        company = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": f"Test Equipment Company {frappe.generate_hash(length=8)}",
            }
        ).insert()
        parent = frappe.get_doc(
            {
                "doctype": "Engineering Project",
                "project_name": f"Test Equipment Parent {frappe.generate_hash(length=8)}",
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
            "equipments",
            {
                "equipment_name": "凿岩台车",
                "quantity": 1,
                "usage_hours": 12.0,
                "actual_hours": 10.0,
                "hourly_rate": 200.0,
            },
        )
        parent.save()

        self.assertEqual(len(parent.equipments), 1)
        self.assertEqual(parent.equipments[0].total_cost, 2000.0)
        parent.delete()
        company.delete()

    def test_required_field(self):
        """equipment_name is required."""
        parent, company = self._parent()
        parent.append(
            "equipments",
            {
                "quantity": 1,
                "usage_hours": 12.0,
            },
        )

        with self.assertRaises(frappe.MandatoryError):
            parent.save()

        parent.delete()
        company.delete()
