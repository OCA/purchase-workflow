# Copyright 2023 ArcheTI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    picking_note = fields.Html()

    @api.model
    def _prepare_picking(self):
        vals = super()._prepare_picking()
        if self.picking_note:
            vals["note"] = self.picking_note
        return vals
