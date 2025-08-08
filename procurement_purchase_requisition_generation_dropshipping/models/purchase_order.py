# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("requisition_id")
    def _onchange_requisition_id(self):
        res = super()._onchange_requisition_id()
        if self.requisition_id and self.requisition_id.procurement_group_id:
            self.group_id = self.requisition_id.procurement_group_id.id
        return res

    def _compute_dest_address_id(self):
        res = super()._compute_dest_address_id()
        # propagate the destination address from the sale order
        for order in self:
            sale = order.requisition_id.procurement_group_id.sale_id
            if sale and order.picking_type_id.code == "dropship":
                order.dest_address_id = sale.partner_shipping_id
        return res

    @api.model
    def _get_picking_type(self, company_id):
        picking_type = super()._get_picking_type(company_id)
        # propagate the picking type from the requisition
        # and prevent using the default one
        if self.requisition_id and self.requisition_id.picking_type_id:
            picking_type = self.requisition_id.picking_type_id
        return picking_type
