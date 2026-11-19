# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_approve_active = fields.Boolean(
        string="Use State 'Approved' in Purchase Orders",
        help="Adds an extra state in purchase orders previous to 'Purchase "
        "Order'. After confirming and approving a purchase order it will "
        "go to state 'Approved'. In this state the incoming shipments "
        "are not created yet and you still can go back to draft. You "
        "can release the creation of the incoming shipments moving the "
        "purchase order to state 'Purchase Order'.",
    )
