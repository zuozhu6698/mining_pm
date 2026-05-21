# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestDepartment(FrappeTestCase):
    def _company(self):
        return frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": f"Test Department Company {frappe.generate_hash(length=8)}",
            }
        ).insert()

    def _department_name(self, suffix: str) -> str:
        return f"Test Department {suffix} {frappe.generate_hash(length=8)}"

    def test_create_success(self):
        """Baseline: create record with required fields."""
        company = self._company()
        doc = frappe.get_doc(
            {
                "doctype": "Department",
                "department_name": self._department_name("A"),
                "company": company.name,
            }
        ).insert()

        self.assertEqual(doc.name, doc.department_name)
        doc.delete()
        company.delete()

    def test_required_field(self):
        """department_name is required."""
        company = self._company()
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {
                    "doctype": "Department",
                    "company": company.name,
                }
            ).insert()
        company.delete()

    def test_self_reference_validation(self):
        """parent_department cannot point to the current department."""
        company = self._company()
        doc = frappe.get_doc(
            {
                "doctype": "Department",
                "department_name": self._department_name("Self"),
                "company": company.name,
            }
        ).insert()

        doc.parent_department = doc.name
        with self.assertRaises(frappe.ValidationError):
            doc.save()

        doc.parent_department = None
        doc.delete()
        company.delete()
