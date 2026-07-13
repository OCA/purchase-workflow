# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_auto_validation_id = fields.Many2one(
        comodel_name="purchase.auto.validation",
        string="Auto Purchase Validation",
        readonly=True,
        copy=False,
        index=True,
    )

    @api.constrains("order_line", "purchase_auto_validation_id")
    def _check_auto_purchase_product(self):
        for order in self:
            rule = order.purchase_auto_validation_id
            if not rule:
                continue
            wrong_lines = order.order_line.filtered(
                lambda line: line.product_id
                and line.product_id.id not in rule._get_covered_product_ids()
            )
            if wrong_lines:
                raise ValidationError(
                    _(
                        "Only products configured in the auto"
                        " purchase validation can be ordered in this "
                        "purchase order. The following products are not allowed: %s"
                    )
                    % ", ".join(wrong_lines.mapped("product_id.display_name"))
                )
