# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.exceptions import UserError  # ValidationError,
from odoo.tests.common import TransactionCase


class TestPurchaseOrderArchive(TransactionCase):
    def setUp(self):
        super().setUp()

        self.purchase_order_obj = self.env["purchase.order"]
        product_id = self.env.ref("product.product_product_9")
        vals = {
            "partner_id": self.env.ref("base.res_partner_1").id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product_id.name,
                        "product_id": product_id.id,
                        "product_qty": 1.0,
                        "product_uom": self.env.ref("uom.product_uom_unit").id,
                        "price_unit": 121.0,
                        "date_planned": datetime.today(),
                    },
                )
            ],
        }
        self.po_draft = self.env["purchase.order"].create(vals)
        self.po_sent = self.env["purchase.order"].create(vals)
        self.po_sent.write({"state": "sent"})
        self.po_to_approve = self.env["purchase.order"].create(vals)
        self.po_to_approve.write({"state": "to approve"})
        self.po_purchase = self.env["purchase.order"].create(vals)
        self.po_purchase.button_confirm()
        self.po_done = self.env["purchase.order"].create(vals)
        self.po_done.button_confirm()
        self.po_done.button_done()
        self.po_cancel = self.env["purchase.order"].create(vals)
        self.po_cancel.button_cancel()

    def test_archive(self):
        with self.assertRaises(UserError):
            self.po_draft.toggle_active()
        with self.assertRaises(UserError):
            self.po_sent.toggle_active()
        with self.assertRaises(UserError):
            self.po_to_approve.toggle_active()
        with self.assertRaises(UserError):
            self.po_purchase.toggle_active()
        self.po_done.toggle_active()
        self.assertEqual(self.po_done.active, False)
        self.po_cancel.toggle_active()
        self.assertEqual(self.po_cancel.active, False)
