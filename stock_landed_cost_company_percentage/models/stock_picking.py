# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _prepare_landed_cost_lines(self, company, amount):
        cost_lines = []
        for line in company.landed_cost_company_line:
            product = line.product_id
            account = (
                product.property_account_expense_id.id or
                product.categ_id.property_account_expense_categ_id.id
            )
            values = {
                'product_id': product.id,
                'split_method': product.split_method,
                'account_id': account,
                'price_unit': float((amount or 0.0) * line.percentage) / 100.0,
                'name': product.name,
            }
            cost_lines.append((0, 0, values))
        return cost_lines

    def _prepare_landed_cost(self, amount):
        return {
            'picking_ids': [(6, 0, [self.id])],
            'account_journal_id': self.company_id.journal_id.id,
            'cost_lines': self._prepare_landed_cost_lines(
                self.company_id, amount)
        }

    def _create_landed_cost(self):
        for pick in self:
            # Only applicable for Receipts
            if pick.picking_type_code == 'incoming':
                total_amount = sum(
                    [x.qty_done * x.move_id.purchase_line_id.price_unit for x
                     in pick.move_line_ids])
                # Create landed cost & validate it
                landed_cost = self.env['stock.landed.cost'].create(
                    pick._prepare_landed_cost(total_amount))
                landed_cost.compute_landed_cost()
                landed_cost.button_validate()
        return True

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        self._create_landed_cost()
        return res
