# Copyright 2020 - Radovan Skolnik <radovan@skolnik.info>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    procured_purchase_grouping = fields.Selection(
        [
            ("standard", "Standard grouping"),
            ("line", "No line grouping"),
            ("order", "No order grouping"),
            ("product_category", "Product category grouping"),
        ],
        default="standard",
        help="Select the behaviour for grouping procured purchases for the "
        "the products of this category:\n"
        "* Standard grouping: Procurements will generate "
        "purchase orders as always, grouping lines and orders when "
        "possible.\n"
        "* No line grouping: If there are any open purchase order for "
        "the same supplier, it will be reused, but lines won't be "
        "merged.\n"
        "* No order grouping: This option will prevent any kind of "
        "grouping.\n"
        "* <empty>: If no value is selected, system-wide default will be used.\n"
        "* Product category grouping: This option groups products in the "
        "same purchase order that belongs to the same product category.",
    )
