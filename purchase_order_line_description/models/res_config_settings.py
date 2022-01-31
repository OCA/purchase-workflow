# Copyright 2015 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - vicent.cubells@tecnativa.com
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _name = 'res.config.settings'
    _inherit = 'res.config.settings'

    group_use_product_description_per_po_line = fields.Selection(
        selection=[
            (0, "Use the product name on the purchase order lines"),
            (1, "Use the product purchase description on the purchase "
                "order lines")
        ],
        string="Order lines description",
        implied_group="purchase_order_line_description."
                      "group_use_product_description_per_po_line",
        help="Allows you to use only product purchase description on the "
        "purchase order lines.",
    )
