# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPurchaseOrderArchive(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order_obj = cls.env["purchase.order"]
        product_id = cls.env.ref("product.product_product_9")
        vals = {
            "partner_id": cls.env.ref("base.res_partner_1").id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product_id.name,
                        "product_id": product_id.id,
                        "product_qty": 1.0,
                        "product_uom": cls.env.ref("uom.product_uom_unit").id,
                        "price_unit": 121.0,
                        "date_planned": datetime.today(),
                    },
                )
            ],
        }
        cls.po_draft = cls.env["purchase.order"].create(vals)
        cls.po_sent = cls.env["purchase.order"].create(vals)
        cls.po_sent.write({"state": "sent"})
        cls.po_to_approve = cls.env["purchase.order"].create(vals)
        cls.po_to_approve.write({"state": "to approve"})
        cls.po_purchase = cls.env["purchase.order"].create(vals)
        cls.po_purchase.button_confirm()
        cls.po_done = cls.env["purchase.order"].create(vals)
        cls.po_done.button_confirm()
        cls.po_done.button_done()
        cls.po_cancel = cls.env["purchase.order"].create(vals)
        cls.po_cancel.button_cancel()

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
