# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEngineeringMaterial(FrappeTestCase):
    def _parent(self):
        company = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": f"Test Material Company {frappe.generate_hash(length=8)}",
            }
        ).insert()
        parent = frappe.get_doc(
            {
                "doctype": "Engineering Project",
                "project_name": f"Test Material Parent {frappe.generate_hash(length=8)}",
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
            "materials",
            {
                "material_name": "锚杆",
                "unit": "kg",
                "planned_qty": 120.0,
                "actual_qty": 100.0,
                "unit_price": 6.0,
            },
        )
        parent.save()

        self.assertEqual(len(parent.materials), 1)
        self.assertEqual(parent.materials[0].total_cost, 600.0)
        parent.delete()
        company.delete()

    def test_required_field(self):
        """material_name is required."""
        parent, company = self._parent()
        parent.append(
            "materials",
            {
                "unit": "kg",
                "planned_qty": 120.0,
            },
        )

        with self.assertRaises(frappe.MandatoryError):
            parent.save()

        parent.delete()
        company.delete()
