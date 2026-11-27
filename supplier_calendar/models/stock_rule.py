# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        res["date_order"] = min(
            value["supplier"].partner_id.supplier_plan_days(
                fields.Datetime.from_string(value["date_planned"])
                - relativedelta(days=company_id.days_to_purchase),
                -1 * value["supplier"].delay,
                company_id,
            )
            for value in values
        )
        return res

    def _get_lead_days(self, product, **values):
        """Give the vendor lead time counted in working days as natural days
        from today, so that the replenishment dates match the order date."""
        buy_rule = self.filtered(lambda r: r.action == "buy")[:1]
        if buy_rule and not self.env.context.get("ignore_vendor_lead_time"):
            seller = (
                values.get("supplierinfo")
                or product.with_company(buy_rule.company_id)._select_seller(
                    quantity=None
                )
            )[:1]
            if seller:
                values["supplierinfo"] = seller._with_natural_delay(buy_rule.company_id)
        return super()._get_lead_days(product, **values)
