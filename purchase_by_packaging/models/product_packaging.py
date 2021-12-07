# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    can_be_purchased = fields.Boolean(
        string="Can be purchased",
        compute="_compute_can_be_purchased",
        readonly=False,
        store=True,
    )

    force_purchase_qty = fields.Boolean(
        string="Force purchase quantity",
        help="Determine if during the creation of a purchase order line, the "
        "quantity should be forced with a multiple of the packaging.\n"
        "Example:\n"
        "You purchase a product by packaging of 5 products.\n"
        "When the user will put 3 as quantity, the system can force the "
        "quantity to the superior unit (5 for this example).",
    )

    purchase_rounding = fields.Float(
        string="Purchase Rounding Precision",
        digits="Product Unit of Measure",
        required=True,
        default=0.1,
        help="The allowed package quantity will be a multiple of this value. "
        "Use 1.0 for a package that cannot be further split.",
    )

    actual_purchase_qty = fields.Float(compute="_compute_actual_purchase_qty")

    @api.depends("purchase_rounding", "qty")
    def _compute_actual_purchase_qty(self):
        for record in self:
            record.actual_purchase_qty = record.purchase_rounding * record.qty

    @api.depends("packaging_type_id")
    def _compute_can_be_purchased(self):
        for record in self:
            record.can_be_purchased = record.packaging_type_id.can_be_purchased
