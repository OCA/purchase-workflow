# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import Form, TransactionCase


class TestPurchaseCancelConfirm(TransactionCase):
    def setUp(self):
        super(TestPurchaseCancelConfirm, self).setUp()
        self.purchase_order_obj = self.env["purchase.order"]
        self.purchase_order = self.purchase_order_obj.create(
            {
                "partner_id": self.env.ref("base.res_partner_12").id,
            }
        )

    def test_01_cancel_confirm_purchase(self):
        """Cancel a document, I expect cancel_reason.
        Then, set to draft, I expect cancel_reason is deleted.
        """
        self.purchase_order.button_confirm()
        # Click reject, cancel confirm wizard will open. Type in cancel_reason
        res = self.purchase_order.button_cancel()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "button_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.purchase_order.cancel_reason, wizard.cancel_reason)
        self.assertEqual(self.purchase_order.state, "cancel")
        # Set to draft
        self.purchase_order.button_draft()
        self.assertEqual(self.purchase_order.cancel_reason, False)
        self.assertEqual(self.purchase_order.state, "draft")
