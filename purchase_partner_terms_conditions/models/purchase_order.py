# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("partner_id")
    def _onchange_partner_id_purchase_conditions(self):
        for rec in self:
            rec.notes = rec.partner_id.purchase_conditions
