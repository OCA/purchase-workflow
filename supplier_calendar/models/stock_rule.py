# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        dates = [fields.Datetime.from_string(value["date_planned"]) for value in values]
        values = values[0]
        partner = values["supplier"].name
        procurement_date_planned = min(dates)
        schedule_date = procurement_date_planned - relativedelta(
            days=company_id.po_lead
        )
        delay = -1 * values["supplier"].delay
        purchase_date = partner.supplier_plan_days(schedule_date, delay)
        res["date_order"] = purchase_date
        return res
