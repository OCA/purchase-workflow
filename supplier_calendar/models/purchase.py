# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from datetime import datetime

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _get_date_planned(self, seller, po=False):
        date_planned = super()._get_date_planned(seller, po)
        company = po.company_id if po else self.order_id.company_id
        if seller and seller.partner_id._get_supplier_calendar(company):
            date_order = po.date_order if po else self.order_id.date_order
            if date_order:
                date_planned = seller.partner_id.supplier_plan_days(
                    date_order, seller.delay, company
                )
            else:
                date_planned = seller.partner_id.supplier_plan_days(
                    datetime.today(), seller.delay, company
                )
        return date_planned
