# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    original_date_planned = fields.Datetime(
        string="Original Expected Arrival",
        compute="_compute_original_date_planned",
        store=True,
        readonly=True,
        tracking=True,
        help="Original Expected Arrival promised by vendor at PO confirmation.",
    )

    @api.depends("order_line.original_date_planned")
    def _compute_original_date_planned(self):
        for order in self:
            dates_list = order.order_line.filtered(
                lambda x: not x.display_type and x.original_date_planned
            ).mapped("original_date_planned")
            if dates_list:
                order.original_date_planned = fields.Datetime.to_string(min(dates_list))
            else:
                order.original_date_planned = False

    def button_confirm(self):
        res = super().button_confirm()
        for pol in self.mapped("order_line"):
            pol.original_date_planned = pol.date_planned
        return res
