# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013 Camptocamp SA
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
from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class BaseAgreementTestMixin(object):
    """Class that contain common behavior for all agreement related unit test classes.

    We use Mixin because we want to have those behaviors on the various
    unit test subclasses provided by OpenERP in test common.

    """

    def commonsetUp(self):
        cr, uid = self.cr, self.uid
        self.agreement_model = self.registry('framework.agreement')
        self.agreement_line_model = self.registry('framework.agreement.line')
        self.now = datetime.strptime(fields.datetime.now(),
                                     DEFAULT_SERVER_DATETIME_FORMAT)
        self.product_id = self.registry('product.product').create(cr, uid,
                                                                  {'name': 'test_1',
                                                                   'list_price': 10.00})
        self.supplier_id = self.registry('res.partner').create(cr, uid, {'name': 'toto',
                                                                         'supplier': 'True'})

    def _map_agreement_to_po(self, agreement, delta_days):
        """Map agreement to dict to be used by PO create"""
        supplier = agreement.supplier_id
        add = self.browse_ref('base.res_partner_3')
        term = supplier.property_supplier_payment_term
        term = term.id if term else False
        start_date = datetime.strptime(agreement.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        date = start_date + timedelta(days=delta_days)
        data = {}
        data['partner_id'] = supplier.id
        data['pricelist_id'] = supplier.property_product_pricelist_purchase.id
        data['dest_address_id'] = add.id
        data['location_id'] = add.property_stock_customer.id
        data['payment_term_id'] = term
        data['origin'] = agreement.name
        data['date_order'] = date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        data['name'] = agreement.name
        return data

    def _map_agreement_to_po_line(self, agreement, qty, order_id):
        """Map agreement to dict to be used by PO line create"""
        data = {}
        data['product_qty'] = qty
        data['product_id'] = agreement.product_id.id
        data['product_uom'] = agreement.product_id.uom_id.id
        data['price_unit'] = agreement.get_price(qty)
        data['name'] = agreement.product_id.name
        data['order_id'] = order_id
        data['date_planned'] = self.now
        return data

    def make_po_from_agreement(self, agreement, qty=0, delta_days=1):
        """Create a purchase order from an agreement

        :param agreement: origin agreement browse record
        :param qty: qty to be used on po line
        :delta days: set date of po to agreement start date + delta

        :returns: purchase order browse record

        """
        cr, uid = self.cr, self.uid
        po_model = self.registry('purchase.order')
        po_line_model = self.registry('purchase.order.line')
        po_id = po_model.create(cr, uid, self._map_agreement_to_po(agreement, delta_days))
        po_line_model.create(cr, uid, self._map_agreement_to_po_line(agreement, qty, po_id))
        return po_model.browse(cr, uid, po_id)
