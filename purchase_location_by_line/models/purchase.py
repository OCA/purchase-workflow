# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models

_USAGE_SELECTION = [('supplier', 'Supplier Location'),
                    ('view', 'View'),
                    ('internal', 'Internal Location'),
                    ('customer', 'Customer Location'),
                    ('inventory', 'Inventory'),
                    ('procurement', 'Procurement'),
                    ('production', 'Production'),
                    ('transit', 'Transit Location')]


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_order_line_move(self, order, order_line, picking_id,
                                 group_id):
        res_list = super(PurchaseOrder, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)

        for res in res_list:
            if order.related_usage != 'customer' and \
                    order_line.location_dest_id:
                res['location_dest_id'] = order_line.location_dest_id.id
        return res_list

    @api.model
    def _get_group_keys(self, order, line, picking_id=False):
        """Define the key that will be used to group. The key should be
        defined as a tuple of dictionaries, with each element containing a
        dictionary element with the field that you want to group by. This
        method is designed for extensibility, so that other modules can add
        additional keys or replace them by others."""
        key = super(PurchaseOrder, self)._get_group_keys(order, line,
                                                         picking_id=picking_id)
        return key + ({'location_dest_id': line.location_dest_id},)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    location_dest_id = fields.Many2one('stock.location',
                                       'Destination',
                                       domain=[('usage', 'in',
                                                ['internal', 'transit'])])
