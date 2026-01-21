# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from odoo.addons.purchase_requisition.tests.common import TestPurchaseRequisitionCommon


@tagged("post_install", "-at_install")
class TestPurchaseRequisitionTierValidation(TestPurchaseRequisitionCommon):
    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "purchase.requisition",
            self.env["tier.definition"]._get_tier_validation_model_names(),
        )

    def test_purchase_requisition_tier_validation(self):
        self.env["tier.definition"].create(
            {
                "definition_domain": "[]",
                "model_id": self.env["ir.model"]._get("purchase.requisition").id,
                "review_type": "individual",
                "reviewer_id": self.user_purchase_requisition_user.id,
            }
        )
        requisition = self.env["purchase.requisition"].create(
            {
                "requisition_type": "blanket_order",
                "vendor_id": self.res_partner_1.id,
                "line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_09.id,
                            "product_qty": 4,
                            "product_uom_id": self.product_uom_id.id,
                            "price_unit": 10,
                        },
                    ),
                ],
            },
        )
        self.assertEqual(requisition.state, "draft")

        # Can't confirm the requisition before the validation
        with self.assertRaisesRegex(
            ValidationError,
            "needs to be validated",
        ):
            with self.env.cr.savepoint():
                requisition.action_confirm()

        # Request validation
        requisition.request_validation()
        requisition.review_ids.invalidate_recordset()  # Ensure correct status
        self.assertEqual(requisition.validation_status, "pending")

        # Validate the requisition
        requisition.with_user(self.user_purchase_requisition_user).validate_tier()
        requisition.invalidate_recordset()  # Ensure need_validation is refreshed
        self.assertEqual(requisition.validation_status, "validated")

        # Now it can be confirmed
        requisition.action_confirm()
        self.assertEqual(requisition.state, "confirmed")
