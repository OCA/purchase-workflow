# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from openerp.tests import common


class TestPurchaseOrder(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()

        self.partner = self.env['res.partner'].search([
            ('supplier', '=', True),
        ], limit=1)

        self.validator = self.env['res.users'].create({
            'login': 'validator',
            'name': 'validator',
            'email': 'test@localhost',
            'groups_id': [
                (4, self.ref('purchase_internal_validation.'
                             'group_purchase_validator'))
            ],
        })

        self.location_id = self.ref('stock.location_procurement')
        self.pricelist_id = self.ref('product.list0')

        self.purchase = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'location_id': self.location_id,
            'pricelist_id': self.pricelist_id,
            'order_line': [(0, 0, {
                'name': 'Test',
                'product_qty': 1,
                'price_unit': 5000,
                'date_planned': datetime.now(),
            })],
        })

        self.env["ir.config_parameter"].set_param(
            "purchase_internal_validation.limit_amount", 5000)

    def test_01_get_action_url(self):
        res = self.purchase.get_action_url()
        self.assertTrue(isinstance(res, (str, unicode)))

    def test_02_get_validator_emails(self):
        res = self.purchase.get_validator_emails()
        self.assertIn('test@localhost', res)

    def test_03_require_validation(self):
        res = self.purchase.test_require_validation()
        self.assertTrue(res)

    def test_04_not_require_validation(self):
        self.purchase.order_line[0].write({'price_unit': 4999})
        res = self.purchase.test_require_validation()
        self.assertFalse(res)

    def test_05_wkf_wait_validation_order(self):
        self.purchase.wkf_wait_validation_order()
        self.assertEquals(self.purchase.state, 'wait_valid')
