# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict
from contextlib import contextmanager

from odoo import _, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @contextmanager
    def _change_date_order_to_compute_date_planned(self):
        # Don't recompute records values
        with self.env.protecting(self._fields, self):
            purchase_order_dates = {}
            for purchase in self:
                purchase_order_dates[purchase.id] = purchase.date_order
                purchase.date_order = purchase.date_approve
            yield
            for purchase in self:
                purchase.date_order = purchase_order_dates[purchase.id]

    def _update_date_planned_at_confirm(self):
        """
        Update the date planned from products configuration (sellers)
        For tracking, post a message if the date has been modified.
        """
        for company, purchases in self.partition("company_id").items():
            if not company.purchase_update_date_planned_at_confirm:
                continue
            purchases_and_dates = defaultdict()
            for purchase in purchases:
                purchases_and_dates[purchase.id] = purchase.date_planned
            with self._change_date_order_to_compute_date_planned():
                self.order_line._compute_price_unit_and_date_planned_and_name()
            for purchase in self:
                if purchase.date_planned != purchases_and_dates[purchase.id]:
                    initial_date = self.env["ir.qweb.field.datetime"].value_to_html(
                        purchases_and_dates[purchase.id], {}
                    )
                    new_date = self.env["ir.qweb.field.datetime"].value_to_html(
                        purchase.date_planned, {}
                    )
                    body = _(
                        "The Planned Date was not up-to-date and has been recomputed "
                        "at confirmation: %(initial_date)s → %(date_planned)s",
                        initial_date=initial_date,
                        date_planned=new_date,
                    )
                    purchase.message_post(body=body)

    def button_confirm(self):
        res = super().button_confirm()
        self._update_date_planned_at_confirm()
        return res
