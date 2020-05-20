# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_picking_ok = fields.Boolean(compute="_compute_is_picking_ok", default=False)

    cost_distribution_ok = fields.Boolean(
        "Must be linked to Landed Costs",
        default=False,
        help="If checked, allow to display Landed Cost buttons",
    )

    cost_distribution_state = fields.Char(
        compute="_compute_cost_distribution_state", default="", store=True,
    )

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        self.cost_distribution_ok = (
            self.partner_id.commercial_partner_id.cost_distribution_ok
        )
        return res

    @api.multi
    def _compute_is_picking_ok(self):
        """Check if at least one of the Purchase Order's pickings is 'assigned' or
        'done' in order to display Landed Costs options"""
        for order in self:
            for picking in order.mapped("picking_ids"):
                if picking.state in ["assigned", "done"]:
                    order.is_picking_ok = True
                    break

    @api.multi
    @api.depends("order_line", "picking_ids.state")
    def _compute_cost_distribution_state(self):
        """Compute the lowest Cost Distribution state of the Cost distribution lines
        related to the Purchase Order in order to display Landed Cost buttons and filter
        Purchase Orders depending on this Cost Distribution state"""

        for order in self:
            lines = self.env["purchase.cost.distribution.line"].search(
                [("purchase_id", "=", order.id)]
            )
            if lines:
                distributions_states = [line.distribution.state for line in lines]
                for state in ["draft", "calculated", "done"]:
                    if state in distributions_states:
                        order.cost_distribution_state = state
                        break
            elif order.is_picking_ok:
                order.cost_distribution_state = "required"

    @api.multi
    def button_confirm(self):
        """Update 'cost_distribution_state' in both Picking and Purchase Order when
        confirming order (and creating picking)"""
        res = super().button_confirm()
        for order in self:
            order._compute_is_picking_ok()
            order._compute_cost_distribution_state()
            for picking in order.mapped("picking_ids"):
                picking._compute_cost_distribution_state()
        return res

    @api.multi
    def action_create_cost_distribution(self):
        self.ensure_one()
        line_obj = self.env["purchase.cost.distribution.line"]
        if not line_obj.search([("purchase_id", "=", self.id)]):
            # Create a new Cost Distribution
            distribution = self.env["purchase.cost.distribution"].create({})
            # Link the Purchase Order's pickings to this new Cost Distribution
            list_picking_ids = []
            for picking in self.mapped("picking_ids"):
                if picking.state in ["assigned", "done"]:
                    list_picking_ids.append(picking.id)
            import_picking_wizard = (
                self.with_context(active_id=distribution.id)
                .env["picking.import.wizard"]
                .create(
                    {
                        "supplier": self.partner_id.id,
                        "pickings": [(6, 0, list_picking_ids)],
                    }
                )
            )
            import_picking_wizard.action_import_picking()
            # Then display the new Cost Distribution form view
            lines = line_obj.search([("purchase_id", "=", self.id)])
            return lines.get_action_purchase_cost_distribution()

    @api.multi
    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env['purchase.cost.distribution.line']
        lines = line_obj.search([('purchase_id', '=', self.id)])
        if lines:
            return lines.get_action_purchase_cost_distribution()
