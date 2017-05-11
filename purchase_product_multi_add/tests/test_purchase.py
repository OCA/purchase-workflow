# -*- coding: utf-8 -*-
# © 2016  Denis Roussel, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tests.common as common


class TestPurchase(common.TransactionCase):

    def setUp(self):
        super(TestPurchase, self).setUp()
        self.model_pip = self.env['purchase.import.products']
        self.product_35 = self.env.ref("product.product_product_9")
        self.product_36 = self.env.ref("product.product_product_11")
        self.supplier = self.env.ref("base.res_partner_12")

    def test_import_product_no_quantity(self):
        """ Create PO
            Import products with no quantity
            Check products are presents
        """

        po = self.env["purchase.order"].create({
            'partner_id': self.supplier.id,
        })

        products = [(6, 0, [self.product_35.id, self.product_36.id])]
        wizard_id = self.model_pip.create({'products': products})

        self.assertEqual(
            len(wizard_id.products), 2, 'Should have two products')
        wizard_id.create_items()
        qty = 8.0
        vals = {
            'quantity': qty
        }
        wizard_id.items.write(vals)
        self.assertEqual(
            wizard_id.items[0].quantity,
            qty, 'Should have same quantity')
        # wizard_id = self.model_pip.browse(wizard_id.id)
        self.assertEqual(len(wizard_id.items), 2, 'Should have two items')
        wizard_id.with_context(
            active_id=po.id, active_model='purchase.order').select_products()

        self.assertEqual(len(po.order_line), 2)
        for line in po.order_line:
            self.assertEqual(line.product_qty, qty)
