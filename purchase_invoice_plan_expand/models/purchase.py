# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    expand = fields.Boolean(
        string="Expand by Group",
        readonly=False,
        help="Expolde each order line into multiple lines by grouping name",
    )
    order_line_summary = fields.One2many(
        comodel_name="purchase.order.line.summary",
        inverse_name="order_id",
        readonly=True,
    )

    @api.constrains("expand")
    def _check_expand(self):
        if self.filtered("expand").invoice_plan_ids.filtered(
            lambda l: not l.expand_group
        ):
            raise ValidationError(
                _("Invoice plan's grouping name(s) are required on expand mode")
            )

    def expand_invoice_plan(self):
        """ Expand (not yet expanded) product lines based on invoice plan """
        for purchase in self:
            for line in purchase.order_line.filtered_domain(
                [("origin_line_id", "=", False), ("product_qty", ">", 0)]
            ):
                purchase.invoice_plan_ids._expand_purchase_line(line)

    def merge_purchase_line(self):
        """ Merge all exploeded product line back to original state """
        for purchase in self:
            # Group by origin_line_id
            origin_lines = purchase.order_line.mapped("origin_line_id")
            for origin_line in origin_lines:
                group_lines = purchase.order_line.filtered_domain(
                    [("origin_line_id", "=", origin_line.id)]
                )
                origin_line.write(
                    {
                        "expand_group": False,
                        "origin_line_id": False,
                        "product_qty": sum(group_lines.mapped("product_qty")),
                    }
                )
                # Delete unused line
                group_lines.filtered_domain([("id", "!=", origin_line.id)]).unlink()

    def remove_invoice_plan(self):
        res = super().remove_invoice_plan()
        self.expand = False
        self.merge_purchase_line()
        return res

    def copy(self, default=None):
        if self.filtered("expand"):
            raise ValidationError(
                _("Duplication not allowed for expanded product lines")
            )
        return super().copy(default=default)

    def write(self, vals):
        """ Auto refresh explosion """
        res = super().write(vals)
        purchases = self.filtered(lambda l: l.use_invoice_plan and l.invoice_plan_ids)
        if purchases:
            if "invoice_plan_ids" in vals:
                # Force both merge and expand
                purchases.merge_purchase_line()
                purchases.expand_invoice_plan()
            if "expand" in vals or "order_line" in vals:
                # Merge or expand
                to_expand = purchases.filtered("expand")
                to_merge = self - to_expand
                to_expand.expand_invoice_plan()
                to_merge.merge_purchase_line()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    expand_group = fields.Char(
        string="Group",
        readonly=True,
    )
    origin_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        readonly=True,
        copy=False,
        help="Reference to origin after expanded. Used to merge lines back to original state",
    )

    def _prepare_account_move_line(self, move=False):
        """ In expand mode, remove lines not in expand group """
        expand = self._context.get("expand")
        invoice_plan_id = self._context.get("invoice_plan_id")
        if expand and invoice_plan_id:
            plan = self.env["purchase.invoice.plan"].browse(invoice_plan_id)
            if self.expand_group and self.expand_group != plan.expand_group:
                return {"force_remove_this": True}
        return super()._prepare_account_move_line(move=move)


class PurchaseInvoicePlan(models.Model):
    _inherit = "purchase.invoice.plan"

    expand_group = fields.Char(
        string="Group",
        help="Split products lines by specified group name, i.e, Fiscal Year",
    )

    def _expand_purchase_line(self, order_line):
        """ For each order line, expand into multi groups """
        Decimal = self.env["decimal.precision"]
        prec = Decimal.precision_get("Product Unit of Measure")
        count = sum_qty = 0
        group_percent = self._get_percent_by_expand_group()
        for group, percent in group_percent.items():
            plan_qty = float_round(self._get_plan_qty(order_line, percent), prec)
            vals = {
                "sequence": count,  # reset count
                "expand_group": group,
                "origin_line_id": order_line.id,
                "product_qty": plan_qty,
            }
            if count == (len(group_percent) - 1):  # Last line
                vals["product_qty"] = order_line.product_qty - sum_qty
                order_line.write(vals)
            else:
                copy_vals = order_line._convert_to_write(order_line.read()[0])
                copy_vals = {
                    k: isinstance(v, list) and [(6, 0, v)] or v
                    for k, v in copy_vals.items()
                }
                copy_vals.update(vals)
                order_line.copy(copy_vals)
            count += 1
            sum_qty += plan_qty

    def _get_percent_by_expand_group(self):
        plans = self.filtered_domain(
            [
                ("expand_group", "!=", False),
                ("invoice_type", "=", "installment"),
            ]
        )
        groups = list(set(plans.mapped("expand_group")))
        group_percent = {x: 0 for x in groups}
        for plan in plans:
            group_percent[plan.expand_group] += plan.percent
        if group_percent and sum(group_percent.values()) != 100:
            raise ValidationError(_("Expand group's percent != 100"))
        keys = sorted(group_percent.keys())
        sorted_group_percent = {k: group_percent[k] for k in keys}
        return sorted_group_percent

    def _update_new_quantity(self, line, percent):
        """ Change to invoice plan percent by its expand group """
        if self.env.context.get("expand"):
            group_percent = self.env.context.get("group_percent")
            percent = self.percent / group_percent[self.expand_group] * 100
            self = self.with_context(invoicable_qty=line.quantity)
        super()._update_new_quantity(line, percent)

    @api.model
    def _get_plan_qty(self, order_line, percent):
        """ Fix small decimal problem, make sure qty not exceed invoicable qty """
        plan_qty = super()._get_plan_qty(order_line, percent)
        if self.env.context.get("expand"):
            inv_qty = self.env.context.get("invoicable_qty")
            plan_qty = inv_qty if plan_qty > inv_qty else plan_qty
        return plan_qty


class PurchaseOrderLineSummary(models.Model):
    _name = "purchase.order.line.summary"
    _description = "Summary of exploded order lines"
    _auto = False
    _order = "order_id, sequence, id"

    order_id = fields.Many2one(
        comodel_name="purchase.order",
    )
    sequence = fields.Integer(
        string="Sequence",
    )
    origin_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="origin_line_id.product_id",
        string="Product",
    )
    name = fields.Text(
        string="Description",
        related="origin_line_id.name",
    )
    product_qty = fields.Float(
        string="Quantity",
    )
    product_uom = fields.Many2one(
        comodel_name="uom.uom",
        related="origin_line_id.product_uom",
        string="UoM",
    )
    price_unit = fields.Float(
        string="Unit Price",
    )
    taxes_id = fields.Many2many(
        comodel_name="account.tax",
        related="origin_line_id.taxes_id",
        string="Taxes",
    )
    price_subtotal = fields.Monetary(
        string="Subtotal",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="order_id.currency_id",
        string="Currency",
    )
    # More fields
    date_planned = fields.Datetime(
        related="origin_line_id.date_planned",
        string="Date Planned",
    )
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        related="origin_line_id.account_analytic_id",
        string="Analytic Account",
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        related="origin_line_id.analytic_tag_ids",
        string="Analytic Tags",
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW purchase_order_line_summary AS (
            select origin_line_id id, origin_line_id, order_id,
                min(sequence) as sequence, sum(product_qty) product_qty,
                sum(product_uom) product_uom, avg(price_unit) price_unit,
                sum(price_subtotal) price_subtotal
            from purchase_order_line
            where origin_line_id is not null
            group by origin_line_id, order_id
            )"""
        )
