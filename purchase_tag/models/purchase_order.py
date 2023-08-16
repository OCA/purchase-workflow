# Copyright 2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    tag_ids = fields.Many2many(
        comodel_name="purchase.tag",
        relation="purchase_order_tag_rel",
        column1="purchase_order_id",
        column2="tag_id",
        string="Tags",
    )
