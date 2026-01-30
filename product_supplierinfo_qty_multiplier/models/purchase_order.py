# Copyright 2026 Binhex - Ariel Barreiros
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    bypass_supplierinfo_qty_multiplier = fields.Boolean(
        string="Bypass vendor pricelist Qty. Multiplier",
        help="If checked, the quantity multiplier defined in the "
        "vendor pricelist will not be applied to the purchase order lines "
        "of this purchase order.",
    )
