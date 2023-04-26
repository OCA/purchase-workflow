# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _get_default_category_qty_split_by_uom(self):
        key = "purchase_ordered_qty_by_product_category.split_by_uom"
        param = self.env["ir.config_parameter"].sudo().get_param(key)
        if param and param.strip().lower() in ("1", "true"):
            return True
        company_id = self.default_get(["company_id"]).get("company_id")
        if company_id:
            company = self.env["res.company"].browse(company_id)
            if company.exists() and company.po_category_qty_split_by_uom:
                return True
        return False

    @api.model
    def _get_default_category_qty_split_by_uom_reference(self):
        split_by_uom = self._get_default_category_qty_split_by_uom()
        if not split_by_uom:
            return False
        key = "purchase_ordered_qty_by_product_category.split_by_uom_reference"
        param = self.env["ir.config_parameter"].sudo().get_param(key)
        if param and param.strip().lower() in ("1", "true"):
            return True
        company_id = self.default_get(["company_id"]).get("company_id")
        if company_id:
            company = self.env["res.company"].browse(company_id)
            if (
                company.exists()
                and company.po_category_qty_split_by_uom
                and company.po_category_qty_split_by_uom_reference
            ):
                return True
        return False

    category_qty_split_by_uom = fields.Boolean(
        default=lambda self: self._get_default_category_qty_split_by_uom()
    )
    category_qty_split_by_uom_reference = fields.Boolean(
        default=lambda self: self._get_default_category_qty_split_by_uom_reference()
    )
    qty_by_product_category_ids = fields.One2many(
        "purchase.order.qty.by.product.category",
        "purchase_order_id",
        readonly=True,
        string="Order Qty By Category",
    )
