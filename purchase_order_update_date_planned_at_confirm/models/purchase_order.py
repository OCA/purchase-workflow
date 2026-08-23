# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    current_date_planned = fields.Datetime(
        compute="_compute_current_date_planned",
    )

    @api.depends("order_line.current_date_planned")
    def _compute_current_date_planned(self):
        """date_planned = the earliest date_planned across all order lines."""
        for order in self:
            dates_list = order.order_line.filtered(
                lambda x: not x.display_type and x.current_date_planned
            ).mapped("current_date_planned")
            if dates_list:
                order.current_date_planned = min(dates_list)
            else:
                order.current_date_planned = False

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
            self.order_line._update_date_planned_at_confirm()
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

    def _get_purchase_order_date_confirm_wizard(self):
        self.ensure_one()
        return {
            "name": _("Purchase Order Date Update Confirmation"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.update.date.confirmation",
            "target": "new",
            "views": [[False, "form"]],
            "context": {
                "default_purchase_order_id": self.id,
            },
        }

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            if (
                order.company_id.purchase_update_date_planned_at_confirm
                and not self.env.context.get("purchase_order_update_date")
            ):
                return self._get_purchase_order_date_confirm_wizard()
        self._update_date_planned_at_confirm()
        return res
