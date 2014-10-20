# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2014 Camptocamp SA
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
from collections import defaultdict

from openerp import models, api
from openerp.tools.translate import _


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def auto_rfq_from_suppliers(self):
        """create purchase orders from registered suppliers for products in the
        requisition.

        The created PO for each supplier will only concern the products for
        which an existing product.supplierinfo record exist for that product.
        """
        po_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        seller_products = defaultdict(set)
        for requisition in self:
            products_without_supplier = []
            for line in requisition.line_ids:
                sellers = line.product_id.product_tmpl_id.seller_ids
                if not sellers:
                    products_without_supplier.append(line.product_id)
                for seller in sellers:
                    seller_products[seller.name.id].add(line.product_id.id)
            if products_without_supplier:
                body = _(u'<p><b>RFQ generation</b></p>'
                         '<p>The following products have no '
                         'registered suppliers and are not included in the '
                         'generated RFQs:<ul>%s</ul></p>')
                body %= ''.join(u'<li>%s</li>' % product.name
                                for product in products_without_supplier)
                self.message_post(body=body,
                                  subject=_(u'RFQ Generation'))
        lines_to_remove = po_line_obj.browse()
        for seller_id, sold_products in seller_products.iteritems():
            po_info = self.make_purchase_order(seller_id)
            # make_purchase_order creates po lines for all the products in the
            # requisition. We need to unlink all the created lines for which
            # the supplier is not an official supplier for the product.
            po_ids = po_info.values()
            for purchase in po_obj.browse(po_ids):
                for line in purchase.order_line:
                    if line.product_id.id not in sold_products:
                        lines_to_remove |= line
        lines_to_remove.unlink()
        return True
