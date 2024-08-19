# Copyright 2015-17 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.exceptions import AccessError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_supplier_code = fields.Char(
        compute="_compute_product_supplier_code", store=True, readonly=False
    )

    @api.depends("partner_id", "product_id")
    def _compute_product_supplier_code(self):
        for line in self:
            code = ""
            supplier_info = line.product_id.seller_ids.filtered(
                lambda s, line=line: (
                    s.product_id == line.product_id and s.partner_id == line.partner_id
                )
            )
            if supplier_info:
                code = supplier_info[0].product_code or ""
            else:
                supplier_info = line.product_id.seller_ids.filtered(
                    lambda s, line=line: (
                        s.product_tmpl_id == line.product_id.product_tmpl_id
                        and s.partner_id == line.partner_id
                    )
                )
                if supplier_info:
                    code = supplier_info[0].product_code or ""
            line.product_supplier_code = code


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _add_supplier_to_product(self):
        res = super()._add_supplier_to_product()
        for line in self.order_line:
            partner = (
                self.partner_id
                if not self.partner_id.parent_id
                else self.partner_id.parent_id
            )
            if partner in line.product_id.seller_ids.mapped("partner_id"):
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom,
                )
                if seller:
                    try:
                        seller["product_code"] = line.product_supplier_code
                    except AccessError:
                        break
        return res
