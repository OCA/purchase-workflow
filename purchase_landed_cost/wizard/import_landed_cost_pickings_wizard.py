# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, fields, models


class ImportLandedCostPickingsWizard(models.TransientModel):
    _name = "import.landed.cost.pickings.wizard"
    _description = "Import landed cost pickings"

    possible_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Possible pickings",
        relation="import_landed_cost_pickings_possible_picking_rel",
    )
    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Pickings",
        relation="import_landed_cost_pickings_wizard_stock_picking_rel",
        domain="[('id', 'in', possible_picking_ids)]",
    )

    @api.model
    def default_get(self, fields_list):
        res = super(ImportLandedCostPickingsWizard, self).default_get(fields_list)
        if "possible_picking_ids" in fields_list:
            expenses = self.env["purchase.cost.distribution.expense"].search([])
            pickings = expenses.mapped("distribution.cost_lines.picking_id")
            res["possible_picking_ids"] = [(6, 0, pickings.ids)]
        return res

    def button_import(self):
        self.ensure_one()
        invoice_id = self.env.context["active_id"]
        dist_lines = self.env["purchase.cost.distribution.line"].search(
            [("picking_id", "in", self.picking_ids.ids)]
        )
        exp_lines = dist_lines.mapped("distribution.expense_lines")
        exp_lines.write({"invoice_id": invoice_id})
