# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    vendor_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
        readonly=True,
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["vendor_id"] = "l.vendor_id"
        return res

    def _group_by_sale(self):
        group_by = super()._group_by_sale()
        group_by += ", l.vendor_id"
        return group_by
