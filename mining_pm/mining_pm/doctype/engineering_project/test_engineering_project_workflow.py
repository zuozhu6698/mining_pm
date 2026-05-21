# Copyright (c) 2026, Mining PM and contributors
# See license.txt

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests.utils import FrappeTestCase


class TestEngineeringProjectWorkflow(FrappeTestCase):
    def setUp(self):
        """Prepare required Company link data."""
        if not frappe.db.exists("Company", "Test Workflow Company"):
            frappe.get_doc(
                {
                    "doctype": "Company",
                    "company_name": "Test Workflow Company",
                }
            ).insert(ignore_permissions=True)

    def _make_project(self, name: str):
        return frappe.get_doc(
            {
                "doctype": "Engineering Project",
                "project_name": name,
                "company": "Test Workflow Company",
                "project_type": "掘进",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
            }
        ).insert(ignore_permissions=True)

    def test_workflow_draft_to_submitted(self):
        """Draft project can be submitted through workflow."""
        doc = self._make_project(f"WF Test 1 {frappe.generate_hash(length=8)}")
        self.assertEqual(doc.status, "Draft")

        apply_workflow(doc, "Submit")
        doc.reload()

        self.assertEqual(doc.status, "Submitted")

    def test_workflow_reject_path(self):
        """Submitted project can be rejected through workflow."""
        doc = self._make_project(f"WF Test Reject {frappe.generate_hash(length=8)}")

        apply_workflow(doc, "Submit")
        apply_workflow(doc, "Reject")
        doc.reload()

        self.assertEqual(doc.status, "Rejected")

    def test_workflow_full_path(self):
        """Project can move through the full happy path workflow."""
        doc = self._make_project(f"WF Test Full {frappe.generate_hash(length=8)}")

        apply_workflow(doc, "Submit")
        apply_workflow(doc, "Approve")
        apply_workflow(doc, "Start Construction")
        apply_workflow(doc, "Complete")
        doc.reload()

        self.assertEqual(doc.status, "Completed")
        self.assertEqual(doc.docstatus, 0)
