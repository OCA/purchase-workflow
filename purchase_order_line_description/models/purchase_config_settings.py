# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    group_use_product_description_per_po_line = fields.Boolean(
        "Allow using only the product purchase description on the purchase "
        "order lines", implied_group="purchase_order_line_description."
        "group_use_product_description_per_po_line",
        help="Allows you to use only product purchase description on the "
        "purchase order lines."
    )
