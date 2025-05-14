# Copyright 2025 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

from odoo.addons.purchase_return.models.purchase_return_order import (
    PurchaseOrderReturn as PurchaseReturn,
)


class PurchaseOrderReturn(models.Model):
    _inherit = "purchase.return.order"

    picking_type_id = fields.Many2one(
        "stock.picking.type",
        "Delivered To",
        states=PurchaseReturn.READONLY_STATES,
        required=True,
        default=lambda self: self._default_picking_type(),
        domain="['|', ('warehouse_id', '=', False), "
        "('warehouse_id.company_id', '=', company_id)]",
        help="This will determine operation type of incoming shipment",
    )

    @api.model
    def _get_picking_type(self, company_id):
        picking_type = self.env["stock.picking.type"].search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not picking_type:
            picking_type = self.env["stock.picking.type"].search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return picking_type[:1]

    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(
            self.env.context.get("company_id") or self.env.company.id
        )
