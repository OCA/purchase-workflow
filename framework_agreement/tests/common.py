# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013, 2014 Camptocamp SA
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
from datetime import datetime, timedelta
from openerp import fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class BaseAgreementTestMixin(object):
    """Class that contain common behavior for all agreement unit test classes.

    We use Mixin because we want to have those behaviors on the various
    unit test subclasses provided by OpenERP in test common.

    """

    def commonsetUp(self):
        self.agreement_model = self.env['framework.agreement']
        self.agreement_pl_model = self.env['framework.agreement.pricelist']
        self.agreement_line_model = self.env['framework.agreement.line']
        self.product = self.env['product.product'].create({
            'name': 'test_1',
            'type': 'product',
            'list_price': 10.00
        })
        self.supplier = self.env.ref('base.res_partner_1')

    def _map_agreement_to_po(self, agreement, delta_days):
        """Map agreement to dict to be used by PO create"""
        supplier = agreement.supplier_id
        address = self.env.ref('base.res_partner_3')
        term = supplier.property_supplier_payment_term
        term = term.id if term else False
        start_date = fields.Date.from_string(agreement.start_date)
        date_order = start_date + timedelta(days=delta_days)

        return {
            'partner_id': supplier.id,
            'pricelist_id': supplier.property_product_pricelist_purchase.id,
            'dest_address_id': address.id,
            'location_id': address.property_stock_customer.id,
            'payment_term_id': term,
            'origin': agreement.name,
            'date_order': fields.Date.to_string(date_order),
            'name': agreement.name,
            'framework_agreement_id': agreement.id,
        }

    def _map_agreement_to_po_line(self, agreement, qty, order_id):
        """Map agreement to dict to be used by PO line create"""
        data = {}
        supplier = agreement.supplier_id
        data['product_qty'] = qty
        data['product_id'] = agreement.product_id.product_variant_ids[0].id
        data['product_uom'] = agreement.product_id.uom_id.id
        currency = supplier.property_product_pricelist_purchase.currency_id
        data['price_unit'] = agreement.get_price(qty, currency=currency)
        data['name'] = agreement.product_id.name
        data['order_id'] = order_id
        data['date_planned'] = fields.date.today()
        return data

    def make_po_from_agreement(self, agreement, qty=0, delta_days=1):
        """Create a purchase order from an agreement

        :param agreement: origin agreement browse record
        :param qty: qty to be used on po line
        :delta days: set date of po to agreement start date + delta

        :returns: purchase order browse record

        """
        po_model = self.env['purchase.order']
        po_line_model = self.env['purchase.order.line']
        po = po_model.create(self._map_agreement_to_po(agreement,
                                                       delta_days))
        po_line_model.create(self._map_agreement_to_po_line(agreement,
                                                            qty, po.id))
        return po_model.browse(po.id)
