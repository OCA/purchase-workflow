# -*- encoding: utf-8 -*-
##############################################################################
#
#    Purchase from Product Tree module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning


class PurchaseFromProduct(models.TransientModel):
    _name = 'purchase.from.product'
    _description = 'Wizard to purchase from product tree'

    line_ids = fields.One2many(
        'purchase.from.product.line', 'parent_id', string='Purchase Lines')

    def default_get(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        assert isinstance(context['active_ids'], list),\
            "context['active_ids'] must be a list"
        assert context['active_model'] == 'product.product',\
            "context['active_model'] must be 'product.product'"
        res = super(PurchaseFromProduct, self).default_get(
            cr, uid, fields_list, context=context)
        res['line_ids'] = []
        for product in self.pool['product.product'].browse(
                cr, uid, context['active_ids'], context=context):
            res['line_ids'].append({
                'product_id': product.id,
                'partner_id': product.seller_id.id or False,
                'qty_available': product.qty_available,
                'outgoing_qty': product.outgoing_qty,
                'incoming_qty': product.incoming_qty,
                'uom_id': product.uom_id.id,
                'uom_po_id': product.uom_po_id.id,
                'qty_to_order': 0.0,
                })
        return res

    @api.model
    def _prepare_purchase_order_vals(self, partner, po_lines):
        polo = self.pool['purchase.order.line']
        ponull = self.env['purchase.order'].browse(False)
        po_vals = {'partner_id': partner.id}
        partner_change_dict = ponull.onchange_partner_id(partner.id)
        po_vals.update(partner_change_dict['value'])
        picking_type_id = self.env['purchase.order']._get_picking_in()
        picking_type_dict = ponull.onchange_picking_type_id(picking_type_id)
        po_vals.update(picking_type_dict['value'])
        order_lines = []
        for product, qty_to_order in po_lines:
            product_change_res = polo.onchange_product_id(
                self._cr, self._uid, [],
                partner.property_product_pricelist_purchase.id,
                product.id, qty_to_order, False, partner.id,
                fiscal_position_id=partner.property_account_position.id,
                context=self.env.context)
            product_change_vals = product_change_res['value']
            taxes_id_vals = []
            if product_change_vals.get('taxes_id'):
                for tax_id in product_change_vals['taxes_id']:
                    taxes_id_vals.append((4, tax_id))
                product_change_vals['taxes_id'] = taxes_id_vals
            order_lines.append(
                [0, 0, dict(product_change_vals, product_id=product.id)])
        po_vals['order_line'] = order_lines
        return po_vals

    @api.multi
    def validate(self):
        assert len(self) == 1, 'Only one recordset'
        wiz = self[0]
        assert wiz.line_ids, 'wizard must have some lines'
        # group by supplier
        po_to_create = {}  # key = partner_id, value = [(product, qty)]
        for line in wiz.line_ids:
            if not line.qty_to_order:
                continue
            if line.partner_id in po_to_create:
                po_to_create[line.partner_id].append(
                    (line.product_id, line.qty_to_order))
            else:
                po_to_create[line.partner_id] = [
                    (line.product_id, line.qty_to_order)]
        new_po_ids = []
        for partner, po_lines in po_to_create.iteritems():
            po_vals = self._prepare_purchase_order_vals(
                partner, po_lines)
            new_po = self.env['purchase.order'].create(po_vals)
            new_po_ids.append(new_po.id)

        if not new_po_ids:
            raise Warning(_('No purchase orders created'))
        action = {
            'name': _('Requests for Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'nodestroy': False,
            'target': 'current',
            'domain': [('id', 'in', new_po_ids)],
        }
        return action


class PurchaseFromProductLine(models.TransientModel):
    _name = 'purchase.from.product.line'
    _description = 'Lines of the wizard to purchase from product tree'

    parent_id = fields.Many2one(
        'purchase.from.product', string='Parent')
    product_id = fields.Many2one(
        'product.product', string='Product', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Supplier')
    qty_available = fields.Float(
        string='Quantity Available',
        digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    outgoing_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    incoming_qty = fields.Float(
        string='Incoming Quantity',
        digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    qty_to_order = fields.Float(
        string='Quantity to Order',
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure', readonly=True)
    uom_po_id = fields.Many2one(
        'product.uom', 'Purchase Unit of Measure', readonly=True)
