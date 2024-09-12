# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged("post_install", "-at_install")
class TestPurchaseOrderSequenceOption(TransactionCase):
    def setUp(self):
        super(TestPurchaseOrderSequenceOption, self).setUp()
        self.PurchaseOrder = self.env["purchase.order"]
        self.product_id = self.env.ref("product.product_product_6")
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.po_vals = {
            "partner_id": self.env.ref("base.res_partner_1").id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id.name,
                        "product_id": self.product_id.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id.uom_po_id.id,
                        "price_unit": 500.0,
                        "date_planned": self.date_planned,
                    },
                ),
            ],
        }
        self.po_seq_opt = self.env.ref(
            "purchase_order_sequence_option.purchase_order_sequence_option"
        )

    def test_purchase_order_sequence_options(self):
        """test with and without sequence option activated"""
        # With sequence option
        self.po_seq_opt.use_sequence_option = True
        self.po = self.PurchaseOrder.create(self.po_vals.copy())
        self.assertIn("PO-1", self.po.name)
        self.po_copy = self.po.copy()
        self.assertIn("PO-1", self.po_copy.name)
        # Without sequence option
        self.po_seq_opt.use_sequence_option = False
        self.po = self.PurchaseOrder.create(self.po_vals.copy())
        self.assertNotIn("PO-1", self.po.name)
        self.po_copy = self.po.copy()
        self.assertNotIn("PO-1", self.po_copy.name)
