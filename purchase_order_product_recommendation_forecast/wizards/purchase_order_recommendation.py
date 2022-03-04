# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class PurchaseOrderRecommendation(models.TransientModel):
    _inherit = "purchase.order.recommendation"

    @api.model
    def _default_year_of_reference(self):
        if len(self._selection_year_of_reference()) > 1:
            return str(fields.Date.today().year - 1)
        return str(fields.Date.today().year)

    year_of_reference = fields.Selection(
        string="Year of reference",
        selection="_selection_year_of_reference",
        default=_default_year_of_reference,
    )

    @api.model
    def _selection_year_of_reference(self):
        """A selection of years from the first delivery"""
        year = fields.Date.today().year
        first_year = self.env["stock.move.line"].search_read(
            [("location_dest_id.usage", "=", "customer"), ("state", "=", "done")],
            ["date"],
            order="date ASC",
            limit=1,
        )
        first_year = first_year and first_year[0].get("date").year or year
        return [(str(x), str(x)) for x in range(year, first_year - 1, -1)]

    @api.onchange("year_of_reference")
    def _generate_year_of_reference_recommendations(self):
        """Trigger the general onchange method"""
        return super()._generate_recommendations()

    def _get_year_of_reference_period(self):
        """We'll compute the deliveries for this period"""
        year_diff_begin = self.date_begin.year - int(self.year_of_reference)
        year_diff_end = self.date_end.year - int(self.year_of_reference)
        year_of_reference_begin = self.date_begin - relativedelta(years=year_diff_begin)
        year_of_reference_end = self.date_end - relativedelta(years=year_diff_end)
        return year_of_reference_begin, year_of_reference_end

    def _get_reference_next_period(self):
        """We'll also compute them for this other period so we can get the
        expected increment"""
        date_begin, date_end = self._get_year_of_reference_period()
        range_days = (date_end - date_begin).days
        next_period_begin = date_end + relativedelta(days=1)
        next_period_end = date_end + relativedelta(days=range_days + 1)
        return next_period_begin, next_period_end

    def _find_move_line(self, src="internal", dst="customer"):
        """Use the year of reference to compute the expected increment for
        a given period. This way, we put a period in the wizard and then
        we compute how it performed in relation to next period. This way
        we can draw a simple forecast expecting a linear progression of
        the product deliveries"""
        found_lines = super()._find_move_line(src, dst)
        if (
            dst != "customer"
            or not self.year_of_reference
            or int(self.year_of_reference) == self.date_begin.year
            or self.env.context.get("period_date_begin")
        ):
            return found_lines
        # The period for the year of reference
        (
            year_of_reference_begin,
            year_of_reference_end,
        ) = self._get_year_of_reference_period()
        # The next period in the same year
        (
            year_of_reference_next_begin,
            year_of_reference_next_end,
        ) = self._get_reference_next_period()
        # Now we gather the move lines for such periods and compute the
        # increments which we'll attach to the final dict
        year_ref_found_lines = self.with_context(
            period_date_begin=year_of_reference_begin,
            period_date_end=year_of_reference_end,
        )._find_move_line(src, dst)
        year_ref_next_period_found_lines = self.with_context(
            period_date_begin=year_of_reference_next_begin,
            period_date_end=year_of_reference_next_end,
        )._find_move_line(src, dst)
        for product_id, found_line in found_lines.items():
            qty_ref_done = year_ref_found_lines.get(product_id, {}).get("qty_done", 0)
            qty_ref_next_done = year_ref_next_period_found_lines.get(
                product_id, {}
            ).get("qty_done", 0)
            # We won't consider as we can't rely on the info if there's no data
            # What if the product didn't exist prior to the next period?
            if not qty_ref_done:
                continue
            increment = qty_ref_next_done / qty_ref_done - 1
            found_line.update({"forecasted_increment": increment})
        return found_lines

    def _prepare_wizard_line(self, vals, order_line=False):
        res = super()._prepare_wizard_line(vals, order_line)
        # What if no qty has been done in the reference period?
        increment = vals.get("forecasted_increment", 0)
        units_forecasted = vals.get("qty_delivered", 0) * (1 + increment)
        units_virtual_available = res.get("units_virtual_available", 0)
        res.update(
            {"forecasted_increment": increment, "units_forecasted": units_forecasted}
        )
        # Force the recommended qty to the forcasted one
        if (
            increment
            and self.year_of_reference
            and int(self.year_of_reference) != self.date_begin.year
        ):
            qty_to_order = abs(min(0, units_virtual_available - units_forecasted))
            res.update(
                {
                    "is_modified": bool(qty_to_order),
                    "units_included": (
                        order_line and order_line.product_qty or qty_to_order
                    ),
                }
            )
        return res


class PurchaseOrderRecommendationLine(models.TransientModel):
    _inherit = "purchase.order.recommendation.line"

    forecasted_increment = fields.Float(
        readonly=True,
    )
    forecasted_increment_text = fields.Char(
        string="% inc.",
        compute="_compute_forecasted_increment_text",
        readonly=True,
    )
    units_forecasted = fields.Float(
        string="Qty recommended",
        readonly=True,
    )

    @api.depends("forecasted_increment")
    def _compute_forecasted_increment_text(self):
        """Human friendly forecasted increment"""
        for line in self:
            if not line.forecasted_increment:
                line.forecasted_increment_text = _(" n/a ")
                continue
            line.forecasted_increment_text = "{:.2f}".format(
                line.forecasted_increment * 100
            )
