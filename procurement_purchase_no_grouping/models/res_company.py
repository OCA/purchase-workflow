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
            ("minimal", "Minimal grouping"),
        ],
        string="Procured purchase grouping",
        default="standard",
        help="Select the default behaviour for grouping procured purchases "
        "for the products (if no grouping is selected for categry):\n"
        "* Standard grouping: Procurements will generate "
        "purchase orders as always, grouping lines and orders when "
        "possible.\n"
        "* No line grouping: If there are any open purchase order for "
        "the same supplier, it will be reused, but lines won't be "
        "merged.\n"
        "* No order grouping: This option will prevent any kind of "
        "grouping.\n"
        "* Product category grouping: This option groups products in the "
        "same purchase order that belongs to the same product category.\n"
        "* Minimal grouping: Will generate separate purchase order "
        "per supplier for each procurement and will keep lines in them.",
    )
