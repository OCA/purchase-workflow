# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestPurchase(common.TransactionCase):
    def setUp(self):
        super(TestPurchase, self).setUp()
        self.model_pip = self.env["purchase.import.products"]
        self.product_5 = self.env.ref("product.product_product_5")
        self.product_6 = self.env.ref("product.product_product_6")
        self.supplier = self.env.ref("base.res_partner_1")

    def test_import_product_no_quantity(self):
        """ Create PO
            Import products with no quantity
            Check products are presents
        """

        po = self.env["purchase.order"].create({"partner_id": self.supplier.id})

        products = [(6, 0, [self.product_5.id, self.product_6.id])]
        wizard_id = self.model_pip.create({"products": products})

        self.assertEqual(len(wizard_id.products), 2, "Should have two products")
        wizard_id.create_items()
        qty = 8.0
        vals = {"quantity": qty}
        wizard_id.items.write(vals)
        self.assertEqual(wizard_id.items[0].quantity, qty, "Should have same quantity")
        self.assertEqual(len(wizard_id.items), 2, "Should have two items")
        wizard_id.with_context(
            active_id=po.id, active_model="purchase.order"
        ).select_products()

        self.assertEqual(len(po.order_line), 2)
        for line in po.order_line:
            self.assertEqual(line.product_qty, qty)
