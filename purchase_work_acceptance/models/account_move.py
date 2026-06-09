# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountMove(models.Model):
    _inherit = "account.move"

    require_wa = fields.Boolean(compute="_compute_require_wa")
    wa_id = fields.Many2one(
        comodel_name="work.acceptance",
        string="WA Reference",
        copy=False,
        readonly=True,
        domain=lambda self: [
            ("state", "=", "accept"),
            ("purchase_id", "=", self._context.get("active_id")),
        ],
        help="To control quantity and unit price of the vendor bill, to be "
        "according to the quantity and unit price of the work acceptance.",
    )

    def _compute_require_wa(self):
        for rec in self:
            enforce_wa = self.env.user.has_group(
                "purchase_work_acceptance.group_enforce_wa_on_invoice"
            )
            rec.require_wa = self.wa_id and enforce_wa

    def _aggregate_qty_by_product(self, lines, qty_field, uom_field):
        """Aggregate quantities by product, converted to the product's base UoM."""
        result = defaultdict(float)
        for line in lines:
            uom = getattr(line, uom_field)
            qty = uom._compute_quantity(
                getattr(line, qty_field), line.product_id.uom_id
            )
            if qty > 0.0:
                result[line.product_id.id] += qty
        return dict(result)

    def _check_quantity_wa(self):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        wa_qty = self._aggregate_qty_by_product(
            self.wa_id.wa_line_ids, "product_qty", "product_uom"
        )
        invoice_qty = self._aggregate_qty_by_product(
            self.invoice_line_ids.filtered(lambda line: line.product_id),
            "quantity",
            "product_uom_id",
        )
        all_products = set(wa_qty.keys()) | set(invoice_qty.keys())
        for product_id in all_products:
            wa = wa_qty.get(product_id, 0.0)
            inv = invoice_qty.get(product_id, 0.0)
            if float_compare(wa, inv, precision_digits=precision) != 0:
                product = self.env["product.product"].browse(product_id)
                raise ValidationError(
                    _(
                        "Quantity mismatch for product '%(product)s': "
                        "WA quantity = %(wa_qty)s, Invoice quantity = %(inv_qty)s",
                        product=product.display_name,
                        wa_qty=wa,
                        inv_qty=inv,
                    )
                )

    def action_post(self):
        for rec in self:
            if not rec.wa_id:
                continue
            rec._check_quantity_wa()
        return super().action_post()

    @api.model
    def create(self, vals):
        if self.env.context.get("wa_id"):
            # When use WA, filter for line with qty != 0, good for deposit too.
            lines = vals.get("invoice_line_ids", [])
            lines = filter(lambda l: len(l) == 3 and l[2].get("quantity") != 0, lines)
            vals["invoice_line_ids"] = list(lines)
        return super().create(vals)
