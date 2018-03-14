# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


def execute_onchange(cls, vals, onchanges_dict):
    for onchange_method, changed_fields in onchanges_dict.items():
        if any(f not in vals for f in changed_fields):
            obj = cls.new(vals)
            getattr(obj, onchange_method)()
            for field in changed_fields:
                if field not in vals and obj[field]:
                    vals[field] = obj._fields[field].convert_to_write(
                        obj[field], obj)


class TestPurchaseManualServiceQuantity(TransactionCase):

    def setUp(self):
        super(TestPurchaseManualServiceQuantity, self).setUp()
        self.cls_purchase_order = self.env['purchase.order']
        self.cls_purchase_order_line = self.env['purchase.order.line']
        self.partner01 = self.env.ref('base.res_partner_12')
        self.product01 = self.env.ref('product.product_product_6')

    def common_test(self):
        self.product01.type = 'service'
        purchase_vals = {
            'partner_id': self.partner01.id
        }
        self.purchase = self.cls_purchase_order.create(purchase_vals)
        purchase_line_vals = {
            'product_id': self.product01.id,
            'product_qty': 1.0,
            'price_unit': 10.0,
            'order_id': self.purchase.id,
        }
        onchanges = {
            'onchange_product_id':
                ['date_planned', 'product_uom', 'price_unit', 'name',
                 'taxes_id'],
        }
        execute_onchange(
            self.cls_purchase_order_line, purchase_line_vals, onchanges)
        self.purchase_line = self.cls_purchase_order_line.create(
            purchase_line_vals)

    def test_2(self):
        self.product01.purchase_manual_received_qty = True
        self.common_test()
        self.assertAlmostEqual(self.purchase_line.qty_received, 0, places=2)
        self.purchase.button_confirm()
        self.assertAlmostEqual(self.purchase_line.qty_received, 0, places=2)
        self.purchase_line.qty_received = 1.0
        self.assertAlmostEqual(self.purchase_line.qty_received, 1.0, places=2)
