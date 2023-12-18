# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models

SELLER_USED_TRIGGER_FIELDS = ["product_qty", "product_uom"]


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    seller_used_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Vendor Pricelist Used",
        readonly=True,
        copy=False,
    )

    def _get_seller_from_line(self, vals=False):
        self.ensure_one()
        product_qty = self.product_qty
        product_uom = self.product_uom
        if vals:
            if vals.get("product_qty", False):
                product_qty = vals["product_qty"]
            if vals.get("product_uom", False):
                product_uom_id = vals["product_uom"]
                product_uom = self.env["uom.uom"].browse(product_uom_id)
        params = {"order_id": self.order_id}
        company_id = self.company_id.id
        seller = self.product_id.with_context(force_company=company_id)._select_seller(
            partner_id=self.partner_id,
            quantity=product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=product_uom,
            params=params,
        )
        return seller

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if not line.product_id or line.invoice_lines:
                continue
            seller = line._get_seller_from_line()
            line.with_context(skip_assign_seller_used=True).write(
                {"seller_used_id": seller and seller.id or False}
            )
        return lines

    def write(self, vals):
        """
        IMPORTANT: We search the Vendor Pricelist just as done in Odoo standard
        on the `_onchange_quantity` method
        """
        if not self.env.context.get("skip_assign_seller_used", False) and set(
            vals.keys()
        ) & set(SELLER_USED_TRIGGER_FIELDS):
            for line in self:
                if not line.product_id or line.invoice_lines:
                    continue
                seller = line._get_seller_from_line(vals)
                line.with_context(skip_assign_seller_used=True).write(
                    {"seller_used_id": seller and seller.id or False}
                )
        return super().write(vals)
