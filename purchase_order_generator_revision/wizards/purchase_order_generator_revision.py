# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseOrderGeneratorRevision(models.TransientModel):
    _name = "purchase.order.generator.revision"
    _description = "Purchase Order Generator Revision"

    order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Order",
        help="Name of the Purchase Order.",
    )
    configurator_id = fields.Many2one(
        comodel_name="purchase.order.generator.configuration",
        related="order_id.configurator_id",
        string="Generator",
        readonly=True,
        help="Configuration with which the Purchase Order is generated.",
    )
    target = fields.Float(
        "Target",
        compute="_compute_target_received_qty",
        help="Number of products that are supposed to be received.",
    )
    received_qty = fields.Float(
        "Received Quantity",
        compute="_compute_target_received_qty",
        help="Quantity of products received from the previously generated "
        "Purchase Order.",
    )
    effective_date = fields.Date(
        "Effective Date",
        required=True,
        help="Date on which the revision factor will be applied.",
    )
    revision_factor = fields.Float(
        "Revision Factor (%)",
        required=True,
        help="Factor that will revise the quantities on the Purchase Order "
             "(in %). You can adjust the quantities either with this factor "
             "or directly with the 'quantity to adjust' field. Changing one "
             "of those 2 fields will automatically calculate the other one.",
        default=100.0,
        digits=(32, 32),
    )
    revision_qty = fields.Integer(
        "Quantity to adjust",
        required=True,
        help="Quantity to add or remove to the Purchase Order. If you want to "
             "receive more products, enter a positive number. If you have "
             "already received too much and want to receive less, enter a "
             "negative number. You can either adjust the quantities with this "
             "field or set a revision factor. Changing one of those 2 fields "
             "will automatically calculate the other one.",
        default=0,
    )
    new_target = fields.Float(
        "New Target",
        help="New expected target. This field will be calculated based on the "
             "revision factor or the revision quantity.",
        readonly=True,
    )
    description = fields.Text(
        "Reason for Revision",
        required=True,
    )

    @api.depends("order_id")
    def _compute_target_received_qty(self):
        """
        Compute quantity stock moves from received (done) pickings
        Compute target from available stock moves.
        """
        self.received_qty = (
            sum(
                sum(l.product_uom_qty for l in p.move_lines)
                for p in self.order_id.picking_ids
                if p.state == "done"
            )
        )
        self.target = (
            sum(
                sum(l.product_uom_qty for l in p.move_lines)
                for p in self.order_id.picking_ids
                if p.state in ["waiting", "confirmed", "assigned"]
            )
        )

    @api.onchange("revision_factor")
    def _onchange_revision_factor(self):
        self.new_target = self.target * self.revision_factor / 100
        self.revision_qty = self.new_target - self.target

    @api.onchange("revision_qty")
    def _onchange_revision_qty(self):
        self.new_target = self.target + self.revision_qty
        if self.target == 0:
            self.revision_factor = 100
        else:
            self.revision_factor = 100 * self.new_target / self.target

    @api.onchange("target")
    def _onchange_target(self):
        self.new_target = self.target
        self.revision_factor = 100
        self.revision_qty = 0

    @api.multi
    def validate(self):
        self.ensure_one()
        for picking in self.order_id.picking_ids:
            if picking.state != 'assigned':
                continue
            for move in picking.move_lines:
                product_uom_qty = move.product_uom_qty * self.revision_factor
                move.write({
                    "product_uom_qty": product_uom_qty
                })
