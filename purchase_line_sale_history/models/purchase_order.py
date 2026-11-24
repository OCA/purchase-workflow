# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from babel.dates import get_month_names

from odoo import api, fields, models
from odoo.tools.misc import babel_locale_parse, get_lang


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sales_history_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Sales History Line",
        copy=False,
        help="Order line whose product sales history is displayed.",
    )
    sales_history_data = fields.Json(
        compute="_compute_sales_history_data",
        export_string_translation=False,
    )

    @api.onchange("order_line")
    def _onchange_order_line_sales_history(self):
        # Line-level onchanges cannot reach sibling lines, so the live
        # exclusivity is handled here. sales_history_line_id round-trips
        # through the client between onchange calls, so it reliably tells
        # which line was active before this change, even before saving.
        active = self.order_line.filtered("show_sales_history")
        prev = self.sales_history_line_id
        # In the onchange environment the lines are NewId records while the
        # many2one holds the real id, so compare through _origin.
        new = (
            active.filtered(lambda line: line != prev and line._origin != prev)[-1:]
            or active[:1]
        )
        (active - new).show_sales_history = False
        self.sales_history_line_id = new

    @api.depends("sales_history_line_id.product_id", "date_order")
    def _compute_sales_history_data(self):
        years_back = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("purchase_line_sale_history.years_back", 2)
        )
        month_names = get_month_names(
            "abbreviated", locale=babel_locale_parse(get_lang(self.env).code)
        )
        months = [month_names[month] for month in range(1, 13)]
        for order in self:
            line = order.sales_history_line_id
            if not line.product_id:
                order.sales_history_data = False
                continue
            order_date = order.date_order or fields.Datetime.now()
            current_year = order_date.year
            years = [current_year - offset for offset in range(years_back + 1)]
            qty_by_month = order._get_sales_history_quantities(
                line.product_id, years[-1], current_year
            )
            data = {}
            for year in years:
                row = []
                for month in range(1, 13):
                    qty = qty_by_month.get((year, month))
                    if qty is None:
                        is_future = year == current_year and month > order_date.month
                        row.append(None if is_future else 0)
                    else:
                        row.append(round(qty, 2))
                data[str(year)] = row
            order.sales_history_data = {
                "product_name": line.product_id.display_name,
                "years": years,
                "months": months,
                "data": data,
            }

    def _get_sales_history_quantities(self, product, year_from, year_to):
        """Return {(year, month): qty} of posted customer invoice quantities
        for ``product``, with credit notes subtracted."""
        base_domain = [
            ("product_id", "=", product.id),
            ("parent_state", "=", "posted"),
            ("date", ">=", fields.Date.to_date(f"{year_from}-01-01")),
            ("date", "<=", fields.Date.to_date(f"{year_to}-12-31")),
        ]
        qty_by_month = {}
        for move_type, sign in (("out_invoice", 1), ("out_refund", -1)):
            groups = self.env["account.move.line"]._read_group(
                base_domain + [("move_id.move_type", "=", move_type)],
                groupby=["date:month"],
                aggregates=["quantity:sum"],
            )
            for month_start, qty in groups:
                key = (month_start.year, month_start.month)
                qty_by_month[key] = qty_by_month.get(key, 0.0) + sign * (qty or 0.0)
        return qty_by_month
