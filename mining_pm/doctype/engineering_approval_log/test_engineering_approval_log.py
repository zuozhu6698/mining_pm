# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEngineeringApprovalLog(FrappeTestCase):
    def _parent(self):
        company = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": f"Test Approval Company {frappe.generate_hash(length=8)}",
            }
        ).insert()
        parent = frappe.get_doc(
            {
                "doctype": "Engineering Project",
                "project_name": f"Test Approval Parent {frappe.generate_hash(length=8)}",
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
            "approval_logs",
            {
                "step": "提交",
                "approver": "Administrator",
                "action": "提交",
                "action_date": "2026-01-01 10:00:00",
            },
        )
        parent.save()

        self.assertEqual(len(parent.approval_logs), 1)
        parent.delete()
        company.delete()

    def test_required_field(self):
        """step is required."""
        parent, company = self._parent()
        parent.append(
            "approval_logs",
            {
                "approver": "Administrator",
                "action": "提交",
                "action_date": "2026-01-01 10:00:00",
            },
        )

        with self.assertRaises(frappe.MandatoryError):
            parent.save()

        parent.delete()
        company.delete()
