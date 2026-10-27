# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountIncoterms(models.Model):
    _inherit = "account.incoterms"

    transit_receipt = fields.Boolean(
        help="Purchases with this incoterm are received through the Incoming "
        "transit of their warehouse.",
    )
