# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEngineeringProject(FrappeTestCase):
    def _get_company(self):
        """Return an existing Company without depending on a fixed fixture name."""
        return frappe.get_all("Company", pluck="name", limit=1)[0]

    def test_create_success(self):
        """Baseline: create record with required fields."""
        doc = frappe.get_doc(
            {
                "doctype": "Engineering Project",
                "project_name": "Test Project A",
                "company": self._get_company(),
                "project_type": "掘进",
                "start_date": "2026-05-20",
                "end_date": "2026-05-30",
            }
        ).insert()

        self.assertTrue(doc.name.startswith("ENG-"))
        doc.delete()

    def test_required_field(self):
        """project_name is required."""
        with self.assertRaises(frappe.MandatoryError):
            frappe.get_doc(
                {
                    "doctype": "Engineering Project",
                    "company": self._get_company(),
                    "project_type": "掘进",
                    "start_date": "2026-05-20",
                    "end_date": "2026-05-30",
                }
            ).insert()

    def test_date_validation(self):
        """end_date cannot be earlier than start_date."""
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc(
                {
                    "doctype": "Engineering Project",
                    "project_name": "Test Project Date Validation",
                    "company": self._get_company(),
                    "project_type": "掘进",
                    "start_date": "2026-05-30",
                    "end_date": "2026-05-20",
                }
            ).insert()
