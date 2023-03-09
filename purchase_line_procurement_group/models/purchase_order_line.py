# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    procurement_group_id = fields.Many2one("procurement.group")

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
        """Do not merge PO lines if procurement group is different or not set."""
        _self = self
        if "group_id" in values:
            pg_id = values.get("group_id", False)
            if pg_id:
                pg_id = pg_id.id
            _self = self.filtered(lambda l: l.procurement_group_id.id == pg_id)
        return super(PurchaseOrderLine, _self)._find_candidate(
            product_id=product_id,
            product_qty=product_qty,
            product_uom=product_uom,
            location_id=location_id,
            name=name,
            origin=origin,
            company_id=company_id,
            values=values,
        )

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        if res and res[0] and "group_id" in res[0]:
            res[0]["group_id"] = (
                self.procurement_group_id.id or self.order_id.group_id.id
            )
        return res

    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        """Add procurement group to values"""
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        procurement_group = values.get("group_id")
        if procurement_group:
            res["procurement_group_id"] = procurement_group.id
        return res
