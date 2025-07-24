# Part of Odoo. See LICENSE file for full copyright and licensing details.

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
            if sale:
                order.dest_address_id = sale.partner_shipping_id
        return res

    @api.model
    def _get_picking_type(self, company_id):
        picking_type = super()._get_picking_type(company_id)
        if self.requisition_id and self.requisition_id.picking_type_id:
            picking_type = self.requisition_id.picking_type_id
        return picking_type
