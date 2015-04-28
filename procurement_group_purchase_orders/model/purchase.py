# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent
#    (<http://www.eficent.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from datetime import datetime
from openerp import SUPERUSER_ID, workflow


class procurement_order(orm.Model):

    _inherit = 'procurement.order'

    _columns = {
        'purchase_line_id': fields.many2one('purchase.order.line',
                                            'Purchase Order Line'),
        'purchase_id': fields.related('purchase_line_id', 'order_id',
                                      type='many2one',
                                      relation='purchase.order',
                                      string='Purchase Order'),
    }

    def _get_product_supplier(self, cr, uid, procurement, context=None):
        ''' returns the main supplier of the procurement's product
        given as argument'''
        supplierinfo = self.pool['product.supplierinfo']
        company_supplier = supplierinfo.search(
            cr, uid, [('product_id', '=', procurement.product_id.id),
                      ('company_id', '=', procurement.company_id.id)],
            limit=1, context=context)
        if company_supplier:
            return supplierinfo.browse(cr, uid, company_supplier[0],
                                       context=context).name
        return procurement.product_id.seller_id

    def _get_po_line_values_from_proc(self, cr, uid, procurement, partner,
                                      company, schedule_date, context=None):
        if context is None:
            context = {}
        uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        prod_obj = self.pool.get('product.product')
        acc_pos_obj = self.pool.get('account.fiscal.position')

        seller_qty = procurement.product_id.seller_qty
        pricelist_id = partner.property_product_pricelist_purchase.id
        uom_id = procurement.product_id.uom_po_id.id
        qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id,
                                   procurement.product_qty, uom_id)
        if seller_qty:
            qty = max(qty, seller_qty)
        price = pricelist_obj.price_get(cr, uid, [pricelist_id],
                                        procurement.product_id.id,
                                        qty, partner.id,
                                        {'uom': uom_id})[pricelist_id]

        # Passing partner_id to context for purchase order line integrity of
        #  Line name
        new_context = context.copy()
        new_context.update({'lang': partner.lang, 'partner_id': partner.id})
        product = prod_obj.browse(cr, uid, procurement.product_id.id,
                                  context=new_context)
        taxes_ids = procurement.product_id.supplier_taxes_id
        taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position,
                                    taxes_ids)
        name = product.partner_ref
        if product.description_purchase:
            name += '\n'+ product.description_purchase

        return {
            'name': name,
            'product_qty': qty,
            'product_id': procurement.product_id.id,
            'product_uom': uom_id,
            'price_unit': price or 0.0,
            'date_planned':
                schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'move_dest_id': procurement.move_id.id,
            'taxes_id': [(6, 0, taxes)],
        }

    def make_po(self, cr, uid, ids, context=None):
        """ Resolve the purchase from procurement, which may result in a
        new PO creation, a new PO line creation or a quantity change on
        existing PO line.
        Note that some operations (as the PO creation) are made as SUPERUSER
        because the current user may not have rights to do it (mto product
        launched by a sale for example)
        @return: dictionary giving for each procurement its related resolving
        PO line.
        """
        # Attention! This method overrides the core implementation, as well
        # as any other implementation of this method done by a third party
        # module.
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid,
                                                    context=context).company_id
        po_obj = self.pool.get('purchase.order')
        po_line_obj = self.pool.get('purchase.order.line')
        seq_obj = self.pool.get('ir.sequence')
        pass_ids = []
        linked_po_ids = []
        for procurement in self.browse(cr, uid, ids, context=context):
            partner = self._get_product_supplier(cr, uid, procurement,
                                                 context=context)
            if not partner:
                self.message_post(
                    cr, uid, [procurement.id],
                    _('There is no supplier associated to product %s')
                    % procurement.product_id.name)
                res[procurement.id] = False
            else:
                schedule_date = self._get_purchase_schedule_date(
                    cr, uid, procurement, company, context=context)
                purchase_date = self._get_purchase_order_date(
                    cr, uid, procurement, company, schedule_date,
                    context=context)
                line_vals = self._get_po_line_values_from_proc(
                    cr, uid, procurement, partner, company, schedule_date,
                    context=context)
                # look for any other draft PO for the same supplier,
                # to attach the new line on instead of creating a new draft one
                available_draft_po_ids = po_obj.search(cr, uid, [
                    ('partner_id', '=', partner.id), ('state', '=', 'draft'),
                    ('location_id', '=', procurement.location_id.id),
                    ('company_id', '=', procurement.company_id.id)],
                    context=context)
                if available_draft_po_ids:
                    po_id = available_draft_po_ids[0]
                    po_rec = po_obj.browse(cr, uid, po_id, context=context)
                    # if the product has to be ordered earlier those in the
                    # existing PO, we replace the purchase date on the order
                    #  to avoid ordering it too late
                    if datetime.strptime(
                            po_rec.date_order,
                            DEFAULT_SERVER_DATE_FORMAT) > purchase_date:
                        po_obj.write(cr, uid, [po_id],
                                     {'date_order': purchase_date.strftime(
                                         DEFAULT_SERVER_DATE_FORMAT)},
                                     context=context)
                    line_vals.update(order_id=po_id)
                    po_line_id = po_line_obj.create(cr, SUPERUSER_ID,
                                                    line_vals, context=context)
                    linked_po_ids.append(procurement.id)
                else:
                    name = seq_obj.get(cr, uid, 'purchase.order') or \
                        _('PO: %s') % procurement.name
                    po_vals = {
                        'name': name,
                        'origin': procurement.origin,
                        'partner_id': partner.id,
                        'location_id': procurement.location_id.id,
                        'warehouse_id': self._get_warehouse(procurement,
                                                            company),
                        'pricelist_id':
                            partner.property_product_pricelist_purchase.id,
                        'date_order': purchase_date.strftime(
                            DEFAULT_SERVER_DATE_FORMAT),
                        'company_id': procurement.company_id.id,
                        'fiscal_position':
                            partner.property_account_position and
                            partner.property_account_position.id or False,
                        'payment_term_id':
                            partner.property_supplier_payment_term.id or False,
                    }
                    po_id = self.create_procurement_purchase_order(
                        cr, SUPERUSER_ID, procurement, po_vals, line_vals,
                        context=context)
                    po_line_id = po_obj.browse(
                        cr, uid, po_id, context=context).order_line[0].id
                    pass_ids.append(procurement.id)
                res[procurement.id] = po_id
                self.write(cr, uid, [procurement.id],
                           {'state': 'running',
                            'purchase_line_id': po_line_id}, context=context)
        if pass_ids:
            self.message_post(cr, uid, pass_ids,
                              body=_("Draft Purchase Order created"),
                              context=context)
        if linked_po_ids:
            self.message_post(
                cr, uid, linked_po_ids,
                body=_("Purchase line created and linked to an existing "
                       "Purchase Order"), context=context)
        return res
