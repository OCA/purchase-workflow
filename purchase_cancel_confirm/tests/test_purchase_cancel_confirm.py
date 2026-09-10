# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseCancelConfirm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.PurchaseOrder = cls.env["purchase.order"]
        # Instances
        cls.partner = cls.env["res.partner"].create({"name": "Test vendor"})
        cls.purchase_order = cls._create_purchase_order()

    @classmethod
    def _create_purchase_order(cls, **kwargs):
        vals = {"partner_id": cls.partner.id}
        vals.update(kwargs)
        return cls.PurchaseOrder.create(vals)

    def _cancel_from_button(self, order):
        """Cancel as the Cancel button of the views does"""
        return order.with_context(cancel_confirm_wizard=True).button_cancel()

    def test_01_cancel_confirm_purchase(self):
        """Cancel a document from the button, I expect cancel_reason.
        Then, set to draft, I expect cancel_reason is deleted.
        """
        self.purchase_order.button_confirm()
        # Click cancel, cancel confirm wizard will open. Type in cancel_reason
        res = self._cancel_from_button(self.purchase_order)
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "button_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        self.assertEqual(self.purchase_order.state, "purchase")
        wizard = Form(self.env["cancel.confirm"].with_context(**ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.purchase_order.cancel_reason, "Wrong information")
        self.assertEqual(self.purchase_order.cancel_by, self.env.user)
        self.assertTrue(self.purchase_order.cancel_date)
        self.assertEqual(self.purchase_order.state, "cancel")
        # Set to draft
        self.purchase_order.button_draft()
        self.assertFalse(self.purchase_order.cancel_confirm)
        self.assertFalse(self.purchase_order.cancel_reason)
        self.assertFalse(self.purchase_order.cancel_by)
        self.assertFalse(self.purchase_order.cancel_date)
        self.assertEqual(self.purchase_order.state, "draft")

    def test_02_cancel_not_from_button(self):
        """Cancellations not coming from the Cancel button are not confirmed,
        so that flows cancelling purchase orders on their own still work.
        """
        self.purchase_order.button_confirm()
        self.purchase_order.button_cancel()
        self.assertEqual(self.purchase_order.state, "cancel")
        self.assertFalse(self.purchase_order.cancel_reason)
