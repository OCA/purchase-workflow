# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.tools.date_utils import relativedelta


@tagged('post_install', '-at_install')
class TestPurchaseOrderApproved(TransactionCase):

    def setUp(self):
        super(TestPurchaseOrderApproved, self).setUp()
        self.company1 = self.env.ref('base.main_company')
        self.company1.purchase_approve_active = True
        self.partner1 = self.env.ref('base.res_partner_1')
        self.product1 = self.env.ref('product.product_product_7')

    def test_purchase_order_approved(self):
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner1.id,
            'order_line': [(0, 0, {
                'name': self.product1.name,
                'product_id': self.product1.id,
                'product_qty': 1,
                'product_uom': self.product1.uom_id.id,
                'price_unit': 100,
                'date_planned': fields.Date.today() + relativedelta(days=10),
            })],
            'company_id': self.company1.id,
        })
        purchase_order.button_approve()
        date_approve = fields.Date.today() + relativedelta(days=-30)
        purchase_order.write({'date_approve': date_approve})
        self.assertEqual(purchase_order.state, 'approved')
        # do the actual confirm action
        purchase_order.button_release()
        self.assertEqual(purchase_order.state, 'purchase')
        self.assertEqual(purchase_order.date_approve, date_approve)
