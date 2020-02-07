# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Purchase Representative',
        track_visibility='onchange',
        default=lambda self: self.env.user,
    )
