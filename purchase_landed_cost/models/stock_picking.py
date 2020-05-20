# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2016 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import api, models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cost_distribution_ok = fields.Boolean(
        related="purchase_id.cost_distribution_ok",
        readonly=True,
        default=False,
        help="If checked, allow to display Landed Cost buttons",
    )

    cost_distribution_state = fields.Char(
        compute="_compute_cost_distribution_state", default="", store=True,
    )

    @api.multi
    @api.depends("state")
    def _compute_cost_distribution_state(self):
        """Compute the lowest Cost Distribution state of the Cost distribution lines
        related to the Picking in order to display Landed Cost buttons and filter
        Pickings depending on this Cost Distribution state"""

        for picking in self:
            lines = self.env["purchase.cost.distribution.line"].search(
                [("picking_id", "=", picking.id)]
            )
            if lines:
                distributions_states = [line.distribution.state for line in lines]
                for state in ["draft", "calculated", "done"]:
                    if state in distributions_states:
                        picking.cost_distribution_state = state
                        break
            elif picking.state in ["assigned", "done"]:
                picking.cost_distribution_state = "required"

    @api.multi
    def action_create_cost_distribution(self):
        self.ensure_one()
        line_obj = self.env["purchase.cost.distribution.line"]
        if not line_obj.search([("picking_id", "=", self.id)]):
            # Create a new Cost Distribution
            distribution = self.env["purchase.cost.distribution"].create({})
            # Link the Picking to this new Cost Distribution
            import_picking_wizard = (
                self.with_context(active_id=distribution.id)
                .env["picking.import.wizard"]
                .create(
                    {"supplier": self.partner_id.id, "pickings": [(6, 0, [self.id])]}
                )
            )
            import_picking_wizard.action_import_picking()
            # Then display the new Cost Distribution form view
            lines = line_obj.search([("picking_id", "=", self.id)])
            return lines.get_action_purchase_cost_distribution()

    @api.multi
    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env['purchase.cost.distribution.line']
        lines = line_obj.search([('picking_id', '=', self.id)])
        if lines:
            return lines.get_action_purchase_cost_distribution()
