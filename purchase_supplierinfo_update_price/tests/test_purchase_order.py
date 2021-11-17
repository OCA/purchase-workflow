# Copyright 2021 Open Source Intergrators (<http://opensourceintegrators.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestPurchaseOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.supplier = cls.env.ref("base.res_partner_3")
        product_obj = cls.env["product.product"]
        cls.product_1 = product_obj.create(
            {
                "name": "Product 1",
                "invoice_policy": "order",
            }
        )
        cls.product_2 = product_obj.create(
            {
                "name": "Test product 2",
                "invoice_policy": "order",
                "seller_ids": [
                    (0, 0, {"name": cls.supplier.id}),
                    (0, 0, {"name": cls.supplier.id, "min_qty": 10}),
                ],
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
            }
        )
        po_model = cls.env["purchase.order.line"]
        cls.po_line_1 = po_model.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "name": "Product 1",
                "product_qty": 1.0,
                "price_unit": 11.0,
            }
        )
        cls.po_line_2 = po_model.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "name": "Product 2 x 1",
                "product_qty": 1.0,
                "price_unit": 12.0,
            }
        )
        cls.po_line_3 = po_model.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "name": "Product 2 x 10",
                "product_qty": 10.0,
                "price_unit": 13.0,
            }
        )

    def test_move_price_unit(self):
        self.assertAlmostEqual(self.product_1.seller_ids[:1].price, 0.0)
        self.purchase_order.button_confirm()
        self.purchase_order.order_line.write({"qty_received": 1.0})
        self.purchase_order.order_line[-1].qty_received = 10.0
        self.purchase_order.action_create_invoice()
        self.assertAlmostEqual(self.product_1.seller_ids[0].price, 11.0)
        self.assertAlmostEqual(self.product_2.seller_ids[0].price, 12.0)
        self.assertAlmostEqual(self.product_2.seller_ids[1].price, 13.0)
