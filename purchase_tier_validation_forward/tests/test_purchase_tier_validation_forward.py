# Copyright 2026 Spearhead
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseTierValidationForward(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.reviewer = new_test_user(
            cls.env,
            login="purchase_forward_reviewer",
            groups="purchase.group_purchase_manager",
        )
        cls.forward_reviewer = new_test_user(
            cls.env,
            login="purchase_forward_next_reviewer",
            groups="purchase.group_purchase_manager",
        )
        cls.env["tier.definition"].create(
            {
                "name": "Purchase order forwarding",
                "model_id": cls.env["ir.model"]._get("purchase.order").id,
                "definition_domain": "[]",
                "review_type": "individual",
                "reviewer_id": cls.reviewer.id,
                "approve_sequence": True,
                "has_forward": True,
            }
        )
        cls.order = cls.env["purchase.order"].create(
            {"partner_id": cls.env["res.partner"].create({"name": "Vendor"}).id}
        )

    def test_forward_button_is_injected_in_purchase_order_form(self):
        arch = self.env["purchase.order"].get_view(view_type="form")["arch"]
        self.assertIn('name="forward_tier"', arch)

    def test_forward_purchase_order_review(self):
        self.order.request_validation()
        order = self.order.with_user(self.reviewer)
        order.invalidate_recordset()
        self.assertTrue(order.can_forward)

        action = order.forward_tier()
        self.env[action["res_model"]].with_user(self.reviewer).with_context(
            **action["context"]
        ).create(
            {
                "forward_reviewer_id": self.forward_reviewer.id,
                "forward_description": "Please review this purchase order",
            }
        ).add_forward()

        order.invalidate_recordset()
        forwarded_review = order.review_ids.filtered(
            lambda review: review.reviewer_id == self.reviewer
        )
        delegated_review = order.review_ids.filtered(
            lambda review: review.reviewer_id == self.forward_reviewer
        )
        self.assertEqual(forwarded_review.status, "forwarded")
        self.assertEqual(delegated_review.status, "pending")
