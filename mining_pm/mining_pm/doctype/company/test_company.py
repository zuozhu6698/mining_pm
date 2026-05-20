# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestCompany(FrappeTestCase):
    def _company_name(self, suffix: str) -> str:
        return f"Test Company {suffix} {frappe.generate_hash(length=8)}"

    def test_create_success(self):
        """Baseline: create record with required fields."""
        doc = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": self._company_name("A"),
            }
        ).insert()

        self.assertEqual(doc.name, doc.company_name)
        doc.delete()

    def test_required_field(self):
        """company_name is required."""
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc({"doctype": "Company"}).insert()

    def test_self_reference_validation(self):
        """parent_company cannot point to the current company."""
        doc = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": self._company_name("Self"),
            }
        ).insert()

        doc.parent_company = doc.name
        with self.assertRaises(frappe.ValidationError):
            doc.save()

        doc.parent_company = None
        doc.delete()
