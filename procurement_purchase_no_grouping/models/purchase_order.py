# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _merge_in_existing_line(self, product_id, product_qty, product_uom,
                                location_id, name, origin, values):
        grouping = product_id.categ_id.procured_purchase_grouping
        if grouping == 'line':
            return False
        return super()._merge_in_existing_line(
            product_id, product_qty, product_uom, location_id, name, origin,
            values)
