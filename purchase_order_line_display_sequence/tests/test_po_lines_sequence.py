# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests import common


class TestPurchaseOrder(common.TransactionCase):
    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        # Useful models
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseOrderLine = self.env["purchase.order.line"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")

        self.product_id_1.categ_id = self.env.ref("product.product_category_1")
        self.product_id_2.categ_id = self.env.ref("product.product_category_1")

    def _create_purchase_order(self):
        po_vals = {
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
                (
                    0,
                    0,
                    {
                        "name": self.product_id_2.name,
                        "product_id": self.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom": self.product_id_2.uom_po_id.id,
                        "price_unit": 250.0,
                    },
                ),
            ],
        }

        return self.PurchaseOrder.create(po_vals)

    def test_purchase_order_line_sequence(self):

        self.po = self._create_purchase_order()

        i = 1
        for line in self.po.order_line:
            self.assertEqual(line.sequence, i)
            i += 1

        self.assertEqual(self.po.max_line_sequence, 3)

        self.po.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_1.name,
                            "product_id": self.product_id_1.id,
                            "product_qty": 15.0,
                            "product_uom": self.product_id_1.uom_po_id.id,
                            "price_unit": 500.0,
                            "order_id": self.po.id,
                        },
                    )
                ],
            }
        )

        self.assertEqual(self.po.order_line[-1].sequence, 3)
