# Copyright 2015 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - vicent.cubells@tecnativa.com
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    config_product_in_purchase_order_lines = fields.Selection(
        [
            ("option 0", "Use the product name on the purchase order lines"),
            (
                "option 1",
                "Use the product purchase description on the purchase " "order lines",
            ),
        ],
        string="Order lines description",
        help="Allows you to use only product purchase description on the "
        "purchase order lines.",
        config_parameter="account.config_product_in_purchase_order_lines",
    )

    group_use_product_description_per_po_line = fields.Boolean(
        "Order lines description",
        implied_group="purchase_order_line_description."
        "group_use_product_description_per_po_line",
    )

    @api.onchange("config_product_in_purchase_order_lines")
    def _onchange_product_purchase(self):
        self.group_use_product_description_per_po_line = (
            False if self.config_product_in_purchase_order_lines == "option 0" else True
        )
