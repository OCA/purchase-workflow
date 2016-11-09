# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestRFQNumber(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestRFQNumber, self).setUp(*args, **kwargs)
        # Objects
        self.obj_purchase_order = self.env['purchase.order']
        self.obj_ir_sequence = self.env['ir.sequence']

        # Data Products
        self.prod_1 = self.env.ref('product.product_product_5')
        self.prod_2 = self.env.ref('product.product_product_8')

        # Data UOM
        self.prod_uom = self.env.ref('product.product_uom_unit')

        # Data Partner
        self.partner = self.ref('base.res_partner_3')

        # Data Location
        self.location = self.ref('stock.stock_location_stock')

        # Data Pricelist
        self.pricelist = self.ref('product.list0')

    def _prepare_purchase_order_data(self):
        date_planned = '2016-01-01'
        data = {
            'partner_id': self.partner,
            'order_line': [
                (0, 0, {'product_id': self.prod_1.id,
                        'name': self.prod_1.name,
                        'product_uom': self.prod_uom.id,
                        'date_planned': date_planned,
                        'price_unit': self.prod_1.standard_price,
                        'product_qty': 2.0}),
                (0, 0, {'product_id': self.prod_2.id,
                        'name': self.prod_2.name,
                        'product_uom': self.prod_uom.id,
                        'date_planned': date_planned,
                        'price_unit': self.prod_2.standard_price,
                        'product_qty': 5.0})
            ]
        }

        return data

    def _create_purchase_order(self):
        data = self._prepare_purchase_order_data()
        purchase_order = self.obj_purchase_order.create(data)

        return purchase_order

    def test_rfq_number(self):
        # Create PO
        purchase_order = self._create_purchase_order()
        # Check RFQ Number
        # Prefix == 'RFQ'
        self.assertEqual('RFQ', purchase_order.name[:3])
        # Check Confirm PO
        # Prefix == 'PO'
        purchase_order.button_confirm()
        self.assertEqual('PO', purchase_order.name[:2])
