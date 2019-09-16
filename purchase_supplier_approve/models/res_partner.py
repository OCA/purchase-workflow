# Copyright 2019 RGB Consulting - Domantas Sidorenkovas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_approval = fields.Selection([
        ('pda', 'Pending approval'),
        ('apd', 'Approved'),
        ('nad', 'Not approved'),
    ], default='pda', readonly=True, track_visibility='onchange',
        help=" * The 'Pending approval' is the default state. In this state the supplier is still pending approval.\n"
             " * The 'Approved' state indicates that this supplier is approved and his purchase quotations can be confirmed.\n"
             " * The 'Not approved' state is used to specify that the supplier information was rejected.\n")
