# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (<http://www.eficent.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _update_picking_from_group_key(self, key):
        """The picking is updated with data from the grouping key.
        This method is designed for extensibility, so that other modules
        can store more data based on new keys."""
        super(StockPicking, self)._update_picking_from_group_key(key)
        for rec in self:
            for key_element in key:
                if ('location_dest_id' in key_element.keys() and
                        key_element['location_dest_id']):
                    rec.location_dest_id = key_element['location_dest_id']
        return False
