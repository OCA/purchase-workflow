# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_only_supplied_product = fields.Boolean(
        string="Order and invoice only supplied products",
        help="If checked, by default you will only be able to select products"
        " that can be supplied by this supplier when creating a supplier"
        " invoice or purchase for it."
        " This value can be changed by invoice or purchase.",
    )
