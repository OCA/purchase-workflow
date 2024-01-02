# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    purchase_invoice_create_security = fields.Boolean(
        string="Enable invoice creation from purchases protection group",
        help="Check this in order to activate the feature that enforce to be "
        "in 'Create Invoice in Purchases' security group to be allowed to create "
        "invoices from purchases.",
    )
