# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class PurchaseRequest(models.Model):

    _inherit = 'purchase.request'

    @api.onchange('picking_type_id', 'warehouse_id')
    def onchange_picking_type_id(self):
        """Fill the warehouse and the location with the defaults of the
        selected picking type.
        """
        if self.picking_type_id:
            self.warehouse_id = self.picking_type_id.warehouse_id
            self.location_id = self.picking_type_id.default_location_dest_id

    location_id = fields.Many2one(
        comodel_name='stock.location', string='Location',
        readonly=True, states={'draft': [('readonly', False)]})
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string='Warehouse',
        readonly=True, states={'draft': [('readonly', False)]})


class PurchaseRequestLine(models.Model):

    _inherit = 'purchase.request.line'

    @api.multi
    def _generate_procurement_order(
            self, location_id=None, warehouse_id=None):
        """
        This method will generate a procurement order based on the
        purchase request line.
        :type location_id: integer
        :param location_id: id of a stock.location. If not set then
        use the location_id of the related purchase.request
        :type warehouse_id: integer
        :param warehouse_id: id of stock.warehouse. If not set then
        use the warehouse_id of the related purchase_request
        :rtype procurement_order_id: integer
        :rparam procurement_order_id: id of the created procurement.order
        """
        self.ensure_one()
        values = self._prepare_procurement_order_values(
            location_id=location_id, warehouse_id=warehouse_id)
        procurement_order_id = self.env['procurement.order'].create(values)
        return procurement_order_id.id

    @api.multi
    def _prepare_procurement_order_values(
            self, location_id=None, warehouse_id=None):
        self.ensure_one()
        r_id = self.request_id
        if not location_id and r_id.location_id:
            location_id = r_id.location_id.id
        if not warehouse_id and r_id.warehouse_id:
            warehouse_id = r_id.warehouse_id.id
        # Totally ensure that you have a location:
        if not location_id:
            warehouse_id = r_id.picking_type_id.warehouse_id.id
            location_id = r_id.picking_type_id.default_location_dest_id.id
        name = self.name or r_id.name
        vals = {
            'name': name,
            'location_id': location_id,
            'warehouse_id': warehouse_id,
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom': self.product_uom_id.id,
            'date_planned': self.date_required,
        }
        return vals

    procurement_state = fields.Selection(
        related='procurement_id.state',
        store=True, readonly=True, string="Procurement State")
