# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchasePlanningRevision(models.TransientModel):
    _name = "purchase.planning.revision"
    _description = "Purchase Planning Revision"

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
        "Quantity",
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
        "Revision Factor",
        required=True,
        help="Factor that will revise the quantities on the Purchase Order.",
    )
    new_target = fields.Float(
        "New Target",
        required=True,
        help="""New expected target.
This field can either be entered before and a revision factor will be \
calculated or will be calculated based on the revision factor.""",
    )
    description = fields.Text(
        "Reason for Revision",
        required=True,
    )

    @api.depends("order_id")
    def _compute_target_received_qty(self):
        """
        Compute target from expected deliveries of the referred products
        Compute quantity stock moves from received (done) pickings
        """
        self.target = (
            sum(l.product_qty for l in self.order_id.order_line) *
            sum(l.quantity_ratio for l in self.configurator_id.line_ids)
        )
        self.received_qty = (
            sum(
                sum(l.product_uom_qty for l in p.move_lines)
                for p in self.order_id.picking_ids
                if p.state == "done"
            )
        )

    @api.onchange("revision_factor")
    def _onchange_revision_factor(self):
        self.new_target = self.target * self.revision_factor

    @api.onchange("new_target")
    def _onchange_new_target(self):
        if self.target != 0.0:
            self.revision_factor = self.new_target / self.target

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
