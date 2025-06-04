# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import SUPERUSER_ID
from odoo.tests import Form, TransactionCase


class TestPurchaseRequestCancelConfirm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_request_obj = cls.env["purchase.request"]
        cls.env["ir.config_parameter"].sudo().set_param(
            "purchase.request.cancel_confirm_disable", "False"
        )
        cls.purchase_request_line_obj = cls.env["purchase.request.line"]
        vals = {
            "picking_type_id": cls.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        cls.purchase_request = cls.purchase_request_obj.create(vals)
        vals = {
            "request_id": cls.purchase_request.id,
            "product_id": cls.env.ref("product.product_product_13").id,
            "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        cls.purchase_request_line_obj.create(vals)

    def test_01_cancel_confirm_purchase_request(self):
        """Cancel a document, I expect cancel_reason.
        Then, set to draft, I expect cancel_reason is deleted.
        """
        self.purchase_request.button_to_approve()
        # Click reject, cancel confirm wizard will open. Type in cancel_reason
        res = self.purchase_request.button_rejected()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "button_rejected")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(**ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.purchase_request.cancel_reason, wizard.cancel_reason)
        self.assertEqual(self.purchase_request.state, "rejected")
        # Set to draft
        self.purchase_request.button_draft()
        self.assertEqual(self.purchase_request.cancel_reason, False)
        self.assertEqual(self.purchase_request.state, "draft")
