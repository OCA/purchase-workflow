# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#               <contact@eficent.com>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class delivery_carrier(orm.Model):
    _inherit = "delivery.carrier"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        if context is None:
            context = {}
        return [(r['id'], r['name']) for r in self.read(
            cr, uid, ids, ['name'], context)]

    def grid_src_dest_get(self, cr, uid, ids, src_id, dest_id, context=None):
        dest = self.pool.get('res.partner').browse(cr, uid, dest_id,
                                                   context=context)
        src = self.pool.get('res.partner').browse(cr, uid, src_id,
                                                  context=context)
        for carrier in self.browse(cr, uid, ids, context=context):
            for grid in carrier.grids_id:
                get_id = lambda x: x.id
                country_ids = map(get_id, grid.country_ids)
                state_ids = map(get_id, grid.state_ids)
                src_country_ids = map(get_id, grid.src_country_ids)
                src_state_ids = map(get_id, grid.src_state_ids)

                if country_ids and dest.country_id.id not in country_ids:
                    continue
                if state_ids and dest.state_id.id not in state_ids:
                    continue
                if grid.zip_from and (dest.zip or '') < grid.zip_from:
                    continue
                if grid.zip_to and (dest.zip or '') > grid.zip_to:
                    continue
                if src_country_ids and src.country_id.id not in \
                        src_country_ids:
                    continue
                if src_state_ids and src.state_id.id not in src_state_ids:
                    continue
                if grid.src_zip_from and (src.zip or '') < grid.src_zip_from:
                    continue
                if grid.src_zip_to and (src.zip or '') > grid.src_zip_to:
                    continue
                return grid.id
        return False


class delivery_grid(orm.Model):
    _inherit = "delivery.grid"

    _columns = {
            'src_country_ids': fields.many2many(
                'res.country', 'delivery_grid_src_country_rel',
                'grid_id', 'country_id', 'Source Countries'),
            'src_state_ids': fields.many2many('res.country.state',
                                              'delivery_grid_src_state_rel',
                                              'grid_id', 'state_id',
                                              'Source States'),
            'src_zip_from': fields.char('Start Source Zip', size=12),
            'src_zip_to': fields.char('To Source Zip', size=12),
    }

    def get_cost(self, cr, uid, id, order, dt, context=None):
        total = 0
        weight = 0
        volume = 0
        product_uom_obj = self.pool.get('product.uom')
        for line in order.order_line:
            if not line.product_id:
                continue
            q = product_uom_obj._compute_qty(cr, uid, line.product_uom.id,
                                             line.product_qty,
                                             line.product_id.uom_id.id)
            total += line.price_subtotal or 0.0
            weight += (line.product_id.weight or 0.0) * q
            volume += (line.product_id.volume or 0.0) * q

        return self.get_cost_from_picking(cr, uid, id, total, weight,
                                          volume, context=context)

    def get_cost_from_picking(self, cr, uid, id, total, weight, volume,
                              context=None):
        grid = self.browse(cr, uid, id, context=context)
        price = 0.0
        ok = False

        for line in grid.line_ids:
            price_dict = {'price': total, 'volume': volume, 'weight': weight,
                          'wv': volume*weight}
            test = eval(line.type+line.operator+str(line.max_value),
                        price_dict)
            if test:
                if line.price_type == 'variable':
                    price = line.standard_price * price_dict[
                        line.variable_factor]
                else:
                    price = line.standard_price
                ok = True
                break
        if not ok:
            raise orm.except_orm(_('No cost available!'),
                                 _('No line matched this product or order '
                                   'in the chosen delivery grid.'))

        return price