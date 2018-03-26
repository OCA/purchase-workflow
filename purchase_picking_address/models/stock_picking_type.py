# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    purchase_delivery_address_id = fields.Many2one(
        'res.partner',
        String='Purchase delivery address',
    )

    @api.onchange('code')
    def _onchange_usage(self):
        self.purchase_delivery_address_id = False
