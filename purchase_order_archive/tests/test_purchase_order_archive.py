# Copyright 2017 ForgeFlow, S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import UserError

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestPurchaseOrderArchive(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.product_a
        cls.partner = cls.partner_a
        cls.po_vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                Command.create(
                    {
                        "name": cls.product.name,
                        "product_id": cls.product.id,
                        "product_qty": 1.0,
                        "product_uom_id": cls.product.uom_id.id,
                        "price_unit": 121.0,
                    }
                )
            ],
        }
        cls.po_draft = cls.env["purchase.order"].create(cls.po_vals)
        cls.po_sent = cls.env["purchase.order"].create(cls.po_vals)
        cls.po_sent.write({"state": "sent"})
        cls.po_to_approve = cls.env["purchase.order"].create(cls.po_vals)
        cls.po_to_approve.write({"state": "to approve"})
        cls.po_purchase = cls.env["purchase.order"].create(cls.po_vals)
        cls.po_purchase.button_confirm()
        cls.po_done = cls.env["purchase.order"].create(cls.po_vals)
        cls.po_done.button_confirm()
        cls.po_done.button_lock()
        cls.po_cancel = cls.env["purchase.order"].create(cls.po_vals)
        cls.po_cancel.button_cancel()

    def test_archive(self):
        with self.assertRaisesRegex(
            UserError, "Only 'Locked' or 'Canceled' orders can be archived"
        ):
            self.po_draft.action_archive()
        with self.assertRaisesRegex(
            UserError, "Only 'Locked' or 'Canceled' orders can be archived"
        ):
            self.po_sent.action_archive()
        with self.assertRaisesRegex(
            UserError, "Only 'Locked' or 'Canceled' orders can be archived"
        ):
            self.po_to_approve.action_archive()
        with self.assertRaisesRegex(
            UserError, "Only 'Locked' or 'Canceled' orders can be archived"
        ):
            self.po_purchase.action_archive()
        self.po_done.action_archive()
        self.assertFalse(self.po_done.active)
        self.po_cancel.action_archive()
        self.assertFalse(self.po_cancel.active)

    def test_check_state_constraint(self):
        """Test that archived orders cannot have their state changed"""
        self.po_done.action_archive()
        self.assertFalse(self.po_done.active)
        with self.assertRaisesRegex(UserError, "This record is currently archived"):
            self.po_done.state = "purchase"
