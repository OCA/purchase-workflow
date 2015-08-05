# -*- coding: utf-8 -*-
#    Author: Nicolas Bessi, Leonardo Pistone
#    Copyright 2013, 2015 Camptocamp SA
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

from openerp import fields
from .common import AgreementTransactionCase


class TestAvailableQty(AgreementTransactionCase):

    def setUp(self):
        super(TestAvailableQty, self).setUp()
        self.ProductLine = self.env['agreement.product.line']

        self.product_line = self.ProductLine.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'quantity': 200,
        })

    def test_nothing_consumed(self):
        self.assertEqual(self.product_line.available_quantity, 200)

    def test_consumption_of_150_units(self):
        po = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'location_id': self.supplier.property_stock_supplier.id,
            'portfolio_id': self.portfolio.id,
            'pricelist_id': self.agreement.id,
        })

        self.env['purchase.order.line'].create({
            'order_id': po.id,
            'product_id': self.product.id,
            'name': self.product.name,
            'product_qty': 150.,
            'price_unit': 10.,
            'date_planned': fields.Date.today(),
        })

        po.signal_workflow('purchase_confirm')
        self.assertEqual(po.state, 'approved')
        self.assertEqual(self.product_line.available_quantity, 50)
