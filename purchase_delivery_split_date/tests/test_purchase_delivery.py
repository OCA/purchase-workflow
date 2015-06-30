# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase


class TestDeliverySingle(TransactionCase):

    def setUp(self):
        super(TestDeliverySingle, self).setUp()
        # Products
        p1 = self.env.ref('product.product_product_15')
        p2 = self.env.ref('product.product_product_25')

        # 2 dates we can use to test the features
        self.date_sooner = '2015-01-01'
        self.date_later = '2015-12-13'

        self.po = self.env['purchase.order'].create({
            'partner_id': self.ref('base.res_partner_3'),
            'location_id': self.ref('stock.stock_location_stock'),
            'pricelist_id': self.ref('purchase.list0'),
            'order_line': [
                (0, 0, {'product_id': p1.id,
                        'name': p1.name,
                        'price_unit': p1.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 42.0}),
                (0, 0, {'product_id': p2.id,
                        'name': p2.name,
                        'price_unit': p2.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 12.0}),
                (0, 0, {'product_id': p1.id,
                        'name': p1.name,
                        'price_unit': p1.standard_price,
                        'date_planned': self.date_sooner,
                        'product_qty': 1.0})]})

    def test_check_single_date(self):
        self.assertEquals(
            len(self.po.picking_ids), 0,
            "There must not be pickings for the PO when draft")

        self.po.signal_workflow('purchase_confirm')
        self.assertEquals(
            len(self.po.picking_ids), 1,
            "There must be 1 picking for the PO when confirmed")
        self.assertEquals(
            self.po.picking_ids[0].min_date[:10], self.date_sooner,
            "The picking must be planned at the expected date")

    def test_check_multiple_dates(self):
        # Change the date of the first line
        self.po.order_line[0].date_planned = self.date_later

        self.assertEquals(
            len(self.po.picking_ids), 0,
            "There must not be pickings for the PO when draft")

        self.po.signal_workflow('purchase_confirm')
        self.assertEquals(
            len(self.po.picking_ids), 2,
            "There must be 2 pickings for the PO when confirmed")

        sorted_pickings = sorted(self.po.picking_ids, key=lambda x: x.min_date)
        self.assertEquals(
            sorted_pickings[0].min_date[:10], self.date_sooner,
            "The first picking must be planned at the soonest date")
        self.assertEquals(
            sorted_pickings[1].min_date[:10], self.date_later,
            "The second picking must be planned at the latest date")
