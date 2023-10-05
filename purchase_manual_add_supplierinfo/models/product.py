# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    ignore_create_from_po = fields.Boolean(string="Skip and move on")

    def update_from_purchase(self):
        purchase = self.env["purchase.order"].browse(
            self._context.get("update_from_po_id", False)
        )
        purchase._check_supplierinfo()
        lines = purchase.order_line.filtered(lambda s: not s.supplierinfo_ok)
        if lines:
            return lines[0].create_missing_supplierinfo()
        else:
            return True

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get("update_from_po_id", False):
            vals_list = [
                vals for vals in vals_list if not vals.get("ignore_create_from_po")
            ]
            if vals_list:
                return super().create(vals_list)
            else:
                # TODO flag line to ignore
                return self
        else:
            res = super().create(vals_list)
            if self._context.get("update_from_po_line_id", False):
                line = self.env["purchase.order.line"].browse(
                    self._context.get("update_from_po_line_id")
                )
                line.order_id._check_supplierinfo()
            return res
