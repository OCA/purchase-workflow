# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseSequenceOption(TransactionCase):
    def setUp(self):
        super(TestPurchaseSequenceOption, self).setUp()
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseOrderLine = self.env["purchase.order.line"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_6")
        self.po_vals = {
            "partner_id": self.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                    },
                ),
            ],
        }
        self.po_seq_opt1 = self.env.ref("purchase_sequence_option.purchase_sequence")

    def test_purchase_sequence_options(self):
        """ test with and without sequence option activated """
        # With sequence option
        self.po_seq_opt1.use_sequence_option = True
        self.po = self.PurchaseOrder.create(self.po_vals.copy())
        self.assertIn("PO-1", self.po.name)
        # Without sequence option
        self.po_seq_opt1.use_sequence_option = False
        self.po = self.PurchaseOrder.create(self.po_vals.copy())
        self.assertNotIn("PO-1", self.po.name)
