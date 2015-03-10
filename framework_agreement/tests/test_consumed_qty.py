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
import openerp.tests.common as test_common
from .common import BaseAgreementTestMixin


class TestAvailableQty(test_common.TransactionCase, BaseAgreementTestMixin):

    """Test the function fields available_quantity"""

    def setUp(self):
        """ Create a default agreement"""
        super(TestAvailableQty, self).setUp()
        self.commonsetUp()
        start_date = date.today() + timedelta(days=10)
        end_date = date.today() + timedelta(days=20)

        self.agreement = self.agreement_model.create({
            'portfolio_id': self.portfolio.id,
            'product_id': self.product.id,
            'start_date': fields.Date.to_string(start_date),
            'end_date': fields.Date.to_string(end_date),
            'delay': 5,
            'quantity': 200,
        })
        pl = self.agreement_pl_model.create(
            {'framework_agreement_id': self.agreement.id,
             'currency_id': self.ref('base.EUR')}
        )

        self.agreement_line_model.create(
            {'framework_agreement_pricelist_id': pl.id,
             'quantity': 0,
             'price': 77.0}
        )
        self.agreement.open_agreement(strict=False)

    def test_00_noting_consumed(self):
        """Test non consumption"""
        self.assertEqual(self.agreement.available_quantity, 200)

    def test_01_150_consumed(self):
        """ test consumption of 150 units"""
        po = self.env['purchase.order'].create(
            self._map_agreement_to_po(self.agreement, delta_days=5))
        self.env['purchase.order.line'].create(
            self._map_agreement_to_po_line(self.agreement, qty=150, po=po))

        po.signal_workflow('purchase_confirm')
        self.assertIn(po.state, 'approved')
        self.assertEqual(self.agreement.available_quantity, 50)

    def _map_agreement_to_po(self, agreement, delta_days):
        """Map agreement to dict to be used by PO create"""
        supplier = agreement.supplier_id
        address = self.env.ref('base.res_partner_3')
        start_date = fields.Date.from_string(agreement.start_date)
        date_order = start_date + timedelta(days=delta_days)

        return {
            'partner_id': supplier.id,
            'pricelist_id': supplier.property_product_pricelist_purchase.id,
            'dest_address_id': address.id,
            'location_id': address.property_stock_customer.id,
            'payment_term_id': supplier.property_supplier_payment_term.id,
            'origin': agreement.name,
            'date_order': fields.Date.to_string(date_order),
            'name': agreement.name,
        }

    def _map_agreement_to_po_line(self, agreement, qty, po):
        """Map agreement to dict to be used by PO line create"""
        supplier = agreement.supplier_id
        currency = supplier.property_product_pricelist_purchase.currency_id
        return {
            'product_qty': qty,
            'product_id': agreement.product_id.product_variant_ids[0].id,
            'product_uom': agreement.product_id.uom_id.id,
            'price_unit': agreement.get_price(qty, currency=currency),
            'name': agreement.product_id.name,
            'order_id': po.id,
            'date_planned': fields.Date.today(),
            'framework_agreement_id': agreement.id,
        }
