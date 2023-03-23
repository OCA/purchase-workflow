# Copyright 2017 Akretion (http://www.akretion.com)
# Copyright 2020 Camptocamp SA
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = ["purchase.order.line", "base.exception.method"]
    _name = "purchase.order.line"

    ignore_exception = fields.Boolean(
        related="order_id.ignore_exception", store=True, string="Ignore Exceptions"
    )

    def _get_main_records(self):
        return self.mapped("order_id")

    @api.model
    def _reverse_field(self):
        return "purchase_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        return records.mapped("order_id")
