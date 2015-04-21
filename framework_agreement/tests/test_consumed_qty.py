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

from datetime import timedelta, date
from openerp import fields
from .common import AgreementTransactionCase
from unittest2 import skip


class TestAvailableQty(AgreementTransactionCase):

    """Test the function fields available_quantity"""

    def setUp(self):
        """ Create a default agreement"""
        super(TestAvailableQty, self).setUp()
        self.ProductLine = self.env['agreement.product.line']

        self.product_line = self.ProductLine.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'quantity': 200,
        })

    def test_00_noting_consumed(self):
        """Test non consumption"""
        self.assertEqual(self.product_line.available_quantity, 200)

    @skip('unported test')
    def test_01_150_consumed(self):
        """ test consumption of 150 units"""
        po = self.env['purchase.order'].create(
            self._map_agreement_to_po(self.agreement, delta_days=5))
        self.env['purchase.order.line'].create(
            self._map_agreement_to_po_line(self.agreement, qty=150, po=po))

        po.signal_workflow('purchase_confirm')
        self.assertIn(po.state, 'approved')
        self.assertEqual(self.agreement.available_quantity, 50)
