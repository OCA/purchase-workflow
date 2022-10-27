# Copyright 2019 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    discount2 = fields.Float(
        string="Discount 2 (%)",
        digits="Discount",
        compute="_compute_discount2",
        store=True,
        readonly=False,
    )
    discount3 = fields.Float(
        string="Discount 3 (%)",
        digits="Discount",
        compute="_compute_discount3",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id")
    def _compute_discount2(self):
        """Apply the default supplier discount of the selected supplier"""
        for record in self:
            record.discount2 = record.partner_id.default_supplierinfo_discount2

    @api.depends("partner_id")
    def _compute_discount3(self):
        """Apply the default supplier discount of the selected supplier"""
        for record in self:
            record.discount3 = record.partner_id.default_supplierinfo_discount3

    @api.model
    def _get_po_to_supplierinfo_synced_fields(self):
        res = super()._get_po_to_supplierinfo_synced_fields()
        res += ["discount2", "discount3"]
        return res
