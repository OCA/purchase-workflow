# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseOrderapproval(TransactionCase):
    def setUp(self):
        super().setUp()
        # Configure Contact Stages
        self.stage_active = self.env.ref("partner_stage.partner_stage_active")
        self.stage_active.is_default = False
        self.stage_active.approved_purchase = True
        self.stage_draft = self.env.ref("partner_stage.partner_stage_draft")
        self.stage_draft.is_default = True
        self.stage_draft.approved_purchase = False
        # Enable demo rules
        self.env.ref("purchase_partner_approval.excep_vendor_approved").active = True
        self.env.ref(
            "purchase_partner_approval.excep_vendor_dropship_approved"
        ).active = True

    def test_flow_purchase_order_approved(self):
        # New Customer is not approved for Purchase
        customer = self.env["res.partner"].create(
            {"name": "A Customer", "candidate_purchase": True}
        )
        self.assertFalse(customer.purchase_ok)
        # Purchase Order for not approved customer can't be confirmed
        # It return a pop up dialog for purchase.exception.confirm
        order = self.env["purchase.order"].create({"partner_id": customer.id})
        res = order.button_confirm()
        self.assertEqual(res["res_model"], "purchase.exception.confirm")
        # Approve the customer for Purchase
        # (consider the case with Tier Validation, and Validate partner stage change)
        if hasattr(customer, "review_ids"):
            customer.request_validation()
            customer.invalidate_cache()  # Needed to refresh review_ids field
            customer.review_ids.write({"status": "approved"})
        customer.stage_id = self.env.ref("partner_stage.partner_stage_active")
        self.assertTrue(customer.purchase_ok)
        # Purchase Order for approved customer can be confirmed
        # (consider the case with Tier Validation, and Validate partner stage change)
        if hasattr(order, "review_ids"):
            order.request_validation()
            order.invalidate_cache()  # Needed to refresh review_ids field
            order.review_ids.write({"status": "approved"})
        order.button_confirm()
        self.assertIn(order.state, ["purchase", "done"])
