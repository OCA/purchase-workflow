# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_threshold = fields.Boolean(
        groups="purchase.group_purchase_manager",
        help="If checked, the system will use the receipt threshold "
        "to determine the invoice method.",
    )
