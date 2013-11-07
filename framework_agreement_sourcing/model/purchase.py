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
from openerp.osv import orm
from . adapter_util import BrowseAdapterMixin


class purchase_order(orm.Model, BrowseAdapterMixin):
    """Add fuction to create PO from source line.
    It maybe goes against you ain't going to need it principe.
    The idea would be to popose a small design proposition
    to be taken back into purchase_requistion_extended module
    or an other base module.

    Then we should extented it to propose an API
    to generate PO from various sources
    """

    _inherit = "purchase.order"

    #------ PO adapter middleware maybe to put in a aside class but not easy in OpenERP context ----
    def _make_purchase_order_from_origin(self, cr, uid, origin, map_fun, map_line_fun,
                                         post_fun=None, post_line_fun=None, context=None):
        """Create a PO browse record from any other record

        :returns: created record ids

        """
        po_id = self._adapt_origin_to_po(cr, uid, origin, map_fun,
                                         post_fun=post_fun, context=context)
        self._adapt_origin_to_po_line(cr, uid, po_id, origin, map_line_fun,
                                      post_fun=post_line_fun,
                                      context=context)
        return po_id

    def _adapt_origin_to_po(self, cr, uid, origin, map_fun,
                            post_fun=None, context=None):
        """PO adapter function

        :returns: created PO id

        """
        model = self.pool['purchase.order']
        data = self._adapt_origin(cr, uid, model, origin, map_fun,
                                  post_fun=post_fun, context=context)
        self._validate_adapted_data(cr, uid, model, data, context=context)
        po_id = self.create(cr, uid, data, context=context)
        if callable(post_fun):
            post_fun(cr, uid, po_id, origin, context=context)
        return po_id

    def _adapt_origin_to_po_line(self, cr, uid, po_id, origin, map_fun,
                                 post_fun=None, context=None):
        """PO line adapter

        :returns: created PO line id

        """
        model = self.pool['purchase.order.line']
        data = self._adapt_origin(cr, uid, model, origin, map_fun,
                                  post_fun=post_fun, context=context)
        data['order_id'] = po_id
        self._validate_adapted_data(cr, uid, model, data, context=context)
        l_id = model.create(cr, uid, data, context=context)
        if callable(post_fun):
            post_fun(cr, uid, l_id, origin, context=context)
        return l_id
