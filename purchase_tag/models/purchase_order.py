# Copyright 2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    tag_ids = fields.Many2many(
        comodel_name="purchase.tag",
        compute="_compute_tag_ids",
        store=True,
        readonly=False,
        relation="purchase_order_tag_rel",
        column1="purchase_order_id",
        column2="tag_id",
        string="Tags",
    )

    @api.depends("order_line.tag_ids")
    def _compute_tag_ids(self):
        # Add the missing tags from order lines ones
        for purchase in self:
            for tag in purchase.order_line.tag_ids:
                if tag not in purchase.tag_ids:
                    purchase.tag_ids |= tag
