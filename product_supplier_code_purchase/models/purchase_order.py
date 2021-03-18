# Copyright 2015-17 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.exceptions import AccessError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_supplier_code = fields.Char(string="Product Supplier Code")

    @api.onchange(
        "partner_id",
        "product_id",
    )
    def _onchange_product_code(self):
        for line in self:
            supplier_info = line.product_id.seller_ids.filtered(
                lambda s: (
                    s.product_id == line.product_id and s.name == line.partner_id
                )
            )
            if supplier_info:
                line.product_supplier_code = supplier_info[0].product_code or ""
            else:
                supplier_info = line.product_id.seller_ids.filtered(
                    lambda s: (
                        s.product_tmpl_id == line.product_id.product_tmpl_id
                        and s.name == line.partner_id
                    )
                )
                if supplier_info:
                    line.product_supplier_code = supplier_info[0].product_code or ""


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _add_supplier_to_product(self):
        super()._add_supplier_to_product()
        for line in self.order_line:
            partner = (
                self.partner_id
                if not self.partner_id.parent_id
                else self.partner_id.parent_id
            )
            if partner in line.product_id.seller_ids.mapped("name"):
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
