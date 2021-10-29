# Copyright 2021 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    purchase_service_grouping = fields.Selection(
        [
            ("product.category", "Product Category"),
            ("product.template", "Product Template"),
            ("product", "Product"),
            ("sale.order", "Sales Order"),
        ],
        string="Purchase Service Grouping",
        help="Grouping policy used to purchase service products from Sales Orders.\n\n"
        "* Sales Order: Group by Sales Order.\n"
        "* Product Category: Group by Product Category.\n"
        "* Product Template: Group by Product Template.\n"
        "* Product: Group by Product.\n"
        "\nGrouping by Supplier will always be applied.",
    )
