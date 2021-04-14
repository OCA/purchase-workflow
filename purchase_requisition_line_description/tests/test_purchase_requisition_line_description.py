# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common, Form


class TestPurchaseRequisitionLineDescription(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseRequisitionLineDescription, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product',
            'standard_price': 10,
            'description_purchase': 'description for purchase',
        })

    def test_onchange_product_id(self):
        with Form(self.env['purchase.requisition']) as purchase_form:
            purchase_form.vendor_id = self.partner
            with purchase_form.line_ids.new() as line_form:
                line_form.product_id = self.product
            self.assertEqual(
                line_form.name,
                self.product.name+'\n'+self.product.description_purchase
            )
