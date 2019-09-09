# Copyright 2019 RGB Consulting - Domantas Sidorenkovas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_approval = fields.Selection([
        ('pda', 'Pending approval'),
        ('apd', 'Approved'),
        ('nad', 'Not approved'),
    ], default='pda', readonly=True, track_visibility='onchange')
