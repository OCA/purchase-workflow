# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
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
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class purchase_delivery_term(orm.Model):
    _name = 'purchase.delivery.term'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'line_ids': fields.one2many(
            'purchase.delivery.term.line', 'term_id', 'Lines', required=True),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True, select=1),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.company'
        )._company_default_get(cr, uid, 'purchase.delivery.term', context=c),
    }

    def is_total_percentage_correct(self, cr, uid, term_ids, context=None):
        for term in self.browse(cr, uid, term_ids, context=context):
            total = 0.0
            for line in term.line_ids:
                total += line.quantity_perc
            if total != 1:
                return False
        return True


class purchase_delivery_term_line(orm.Model):

    _name = 'purchase.delivery.term.line'
    _rec_name = 'term_id'
    _columns = {
        'term_id': fields.many2one(
            'purchase.delivery.term', 'Term', ondelete='cascade'),
        'quantity_perc': fields.float(
            'Quantity percentage',
            required=True, help="For 20% set '0.2'",
            digits_compute=dp.get_precision('Purchase Delivery Term')),
        'delay': fields.float(
            'Delivery Lead Time', required=True,
            help="Number of days between the order confirmation and the "
            "shipping of the products from the supplier"),
    }


class purchase_order_line_master(orm.Model):

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, context=None):
        return self.pool.get('purchase.order.line').onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order,
            fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, context=context)

    def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty,
                             uom_id, partner_id, date_order=False,
                             fiscal_position_id=False, date_planned=False,
                             name=False, price_unit=False, context=None):
        return self.pool.get('purchase.order.line').onchange_product_uom(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order,
            fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, context=context)

    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(
                cr, uid, line.taxes_id, line.price_unit, line.product_qty)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _name = 'purchase.order.line.master'
    _columns = {
        'order_id': fields.many2one(
            'purchase.order', 'Order Reference',
            select=True, required=True, ondelete='cascade'),
        'delivery_term_id': fields.many2one(
            'purchase.delivery.term',
            'Delivery term', required=True, ondelete='restrict'),
        'name': fields.char(
            'Description', size=256, required=True),
        'product_id': fields.many2one(
            'product.product', 'Product',
            domain=[('purchase_ok', '=', True)], change_default=True),
        'price_unit': fields.float(
            'Unit Price', required=True,
            digits_compute=dp.get_precision('Product Price')),
        'price_subtotal': fields.function(
            _amount_line, string='Subtotal',
            digits_compute=dp.get_precision('Product Price')),
        'product_qty': fields.float(
            'Quantity',
            digits_compute=dp.get_precision('Product UoM'),
            required=True),
        'product_uom': fields.many2one(
            'product.uom', 'Product UOM', required=True),
        'order_line_ids': fields.one2many('purchase.order.line',
                                          'master_line_id', 'Detailed lines'),
        'taxes_id': fields.many2many(
            'account.tax', 'purchase_master_order_line_tax', 'ord_line_id',
            'tax_id', 'Taxes'),
        'date_planned': fields.date(
            'Scheduled Date', required=True, select=True),
    }
    _defaults = {
        'product_qty': 1.0,
    }

    def _prepare_order_line(self, cr, uid, term_line, master_line,
                            group_index=0, context=None):
        order_line_pool = self.pool.get('purchase.order.line')
        group_pool = self.pool.get('purchase.order.line.group')
        group_ids = group_pool.search(cr, uid, [])
        product_qty = master_line.product_qty * term_line.quantity_perc
        order_line_vals = {}
        on_change_res = order_line_pool.onchange_product_id(
            cr, uid, [],
            master_line.order_id.pricelist_id.id,
            master_line.product_id.id,
            master_line.product_qty, master_line.product_uom.id,
            master_line.order_id.partner_id.id,
            date_order=master_line.order_id.date_order,
            fiscal_position_id=master_line.order_id.fiscal_position.id,
            date_planned=master_line.date_planned,
            name=master_line.name, price_unit=master_line.price_unit,
            context=context)
        order_line_vals.update(on_change_res['value'])
        date_planned = datetime.strptime(
            master_line.date_planned, DEFAULT_SERVER_DATE_FORMAT
        ) + timedelta(term_line.delay)
        order_line_vals.update({
            'order_id': master_line.order_id.id,
            'name': master_line.name,
            'price_unit': master_line.price_unit,
            'product_qty': product_qty,
            'product_uom': master_line.product_uom.id,
            'product_id': master_line.product_id.id
            if master_line.product_id
            else False,
            'master_line_id': master_line.id,
            'date_planned': date_planned,
            'picking_group_id': group_ids[group_index],
            'taxes_id': [(6, 0, [tax.id for tax in master_line.taxes_id])],
        })
        return order_line_vals

    def generate_detailed_lines(self, cr, uid, ids, context=None):
        group_pool = self.pool.get('purchase.order.line.group')
        order_line_pool = self.pool.get('purchase.order.line')
        group_ids = group_pool.search(cr, uid, [])
        for master_line in self.browse(cr, uid, ids):
            if master_line.order_line_ids:
                raise orm.except_orm(
                    _('Error'),
                    _("Detailed lines generated yet (for master line '%s'). "
                      "Remove them first") % master_line.name)
            if len(master_line.delivery_term_id.line_ids) > len(group_ids):
                raise orm.except_orm(
                    _('Error'),
                    _("Delivery term lines are %d. Order line groups are %d. "
                      "Please create more groups")
                    % (len(master_line.delivery_term_id.line_ids),
                       len(group_ids)))
            if not master_line.delivery_term_id.is_total_percentage_correct():
                raise orm.except_orm(
                    _('Error'),
                    _("Total percentage of delivery term %s is not equal to 1")
                    % master_line.delivery_term_id.name)
            for group_index, term_line in enumerate(
                master_line.delivery_term_id.line_ids
            ):
                order_line_vals = self._prepare_order_line(
                    cr, uid, term_line, master_line, group_index=group_index,
                    context=context)
                order_line_pool.create(cr, uid, order_line_vals,
                                       context=context)
        return True

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'order_line_ids': [],
        })
        return super(purchase_order_line_master, self).copy_data(
            cr, uid, id, default, context=context)

    def check_master_line_total(self, cr, uid, ids, context=None):
        for master_line in self.browse(cr, uid, ids, context):
            master_qty = master_line.product_qty
            total_qty = 0.0
            for order_line in master_line.order_line_ids:
                total_qty += order_line.product_qty
            if master_qty != total_qty:
                raise orm.except_orm(_('Error'), _(
                    'Order lines total quantity %s is different from master '
                    'line quantity %s') % (total_qty, master_qty))


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'master_line_id': fields.many2one(
            'purchase.order.line.master', 'Master Line'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'master_line_id': False})
        return super(purchase_order_line, self).copy_data(
            cr, uid, id, default, context=context)


class purchase_order(orm.Model):
    _inherit = 'purchase.order'
    _columns = {
        'master_order_line': fields.one2many(
            'purchase.order.line.master', 'order_id', 'Master Order Lines',
            readonly=True,
            states={'draft': [('readonly', False)]}),
        }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'order_line': [],
        })
        return super(purchase_order, self).copy(
            cr, uid, id, default, context=context)

    def generate_detailed_lines(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            for master_line in order.master_order_line:
                master_line.generate_detailed_lines()
        return True

    def wkf_approve_order(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            for master_line in order.master_order_line:
                master_line.check_master_line_total()
        return super(purchase_order, self).wkf_approve_order(
            cr, uid, ids, context=context)
