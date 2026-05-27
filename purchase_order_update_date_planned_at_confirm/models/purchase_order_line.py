# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    current_date_planned = fields.Datetime(
        compute="_compute_current_date_planned",
    )

    @contextmanager
    def _change_date_order_to_compute_date_planned(self, current_date=False):
        # Don't recompute records values
        with self.env.protecting(self._fields, self):
            purchase_order_dates = {}
            for purchase in self.order_id:
                purchase_order_dates[purchase.id] = (
                    current_date if current_date else purchase.date_order
                )
                purchase.date_order = purchase.date_approve
            yield
            for purchase in self.order_id:
                purchase.date_order = purchase_order_dates[purchase.id]

    @api.depends(
        "order_id.date_order", "product_id", "product_uom", "partner_id", "product_qty"
    )
    def _compute_current_date_planned(self):
        """
        Mimic here the Odoo code '_compute_price_unit_and_date_planned_and_name()'
        function but only for date_planned field.
        """
        for line in self:
            params = line._get_select_sellers_params()
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order
                and line.order_id.date_order.date()
                or fields.Date.context_today(line),
                uom_id=line.product_uom,
                params=params,
            )

            if seller:
                with self._change_date_order_to_compute_date_planned(
                    current_date=fields.Date.context_today(line)
                ):
                    date_planned = line._get_date_planned(seller).strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT
                    )
                line.current_date_planned = date_planned
            else:
                line.current_date_planned = False

    def _update_date_planned_at_confirm(self):
        with self._change_date_order_to_compute_date_planned():
            for line in self:
                if not line.product_id or line.invoice_lines or not line.company_id:
                    continue
                line.date_planned = line.current_date_planned
