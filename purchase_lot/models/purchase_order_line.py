# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    lot_id = fields.Many2one("stock.lot", string="Serial Number", copy=False)
    tracking = fields.Selection(related="product_id.tracking")

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        vals = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        lot_id = values.get("restrict_lot_id")
        if lot_id:
            vals["lot_id"] = lot_id
        return vals

    def _prepare_stock_move_vals(
        self, picking, price_unit, product_uom_qty, product_uom
    ):
        vals = super()._prepare_stock_move_vals(
            picking, price_unit, product_uom_qty, product_uom
        )
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    def _find_candidate(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        lot_id = values.get("restrict_lot_id", False)
        self = self.filtered(lambda line: line.lot_id.id == lot_id)
        return super()._find_candidate(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
