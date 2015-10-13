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


class purchase_order_line_group(orm.Model):
    _name = 'purchase.order.line.group'
    _columns = {
        'name': fields.char('Group', size=64, required=True),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True, select=1),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.company'
        )._company_default_get(
            cr, uid, 'purchase.order.line.group', context=c
        ),
    }


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'picking_group_id': fields.many2one(
            'purchase.order.line.group',
            'Group',
            help="This is used by 'multi-picking' to group order lines in one "
            "picking"),
        }


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def action_picking_create(self, cr, uid, ids, context=None):
        picking_pool = self.pool.get('stock.picking')
        picking_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            lines_by_group = {}
            for line in order.order_line:
                group_id = (
                    line.picking_group_id.id
                    if line.picking_group_id
                    else 0
                )
                lines_by_group.setdefault(group_id, []).append(line)
            for group in lines_by_group:
                if not group:
                    picking_id = None
                else:
                    picking_vals = super(
                        purchase_order, self
                    )._prepare_order_picking(
                        cr, uid, order, context=context
                    )
                    picking_id = picking_pool.create(
                        cr, uid, picking_vals, context=context)
                picking_ids.extend(
                    super(purchase_order, self)._create_pickings(
                        cr, uid, order, lines_by_group[group], picking_id,
                        context=context))
        return picking_ids[0] if picking_ids else False  # ?
