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
        """Do no merge PO lines if procurement group is different."""
        if "group_id" in values:
            lines = self.filtered(
                lambda l: l.procurement_group_id == values["group_id"]
            )
        else:
            lines = self
        return super(PurchaseOrderLine, lines)._find_candidate(
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
