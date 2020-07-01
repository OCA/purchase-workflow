# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common
from odoo.tools import SUPERUSER_ID


class TestPurchaseRequestToRfq(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestToRfq, self).setUp()
        self.purchase_request = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']
        self.wiz =\
            self.env['purchase.request.line.make.purchase.order']
        self.purchase_order = self.env['purchase.order']
        self.account = self.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id
        })
        self.usage = self.env['purchase.product.usage'].create({
            'name': 'Personal',
            'code': 'Ps',
            'account_id': self.account.id
        })

    def test_purchase_request_to_purchase_rfq(self):
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request.id,
            'usage_id': self.usage.id,
            'product_id': self.env.ref('product.product_product_13').id,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'product_qty': 5.0,
        }
        purchase_request_line = self.purchase_request_line.create(vals)
        purchase_request.button_to_approve()
        purchase_request.button_approved()

        vals = {
            'supplier_id': self.env.ref('base.res_partner_12').id,
        }
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line.id],
            active_id=purchase_request_line.id).create(vals)
        wiz_id.make_purchase_order()
        self.assertTrue(
            purchase_request_line.purchase_lines.mapped('usage_id'),
            'Should pass usage')
