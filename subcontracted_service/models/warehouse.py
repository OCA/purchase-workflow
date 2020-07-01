# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    subcontracting_service_proc_rule_id = fields.Many2one(
        comodel_name='stock.rule',
        string="Subcontracting Service Procurement Rule"
    )

    def _get_buy_route(self):
        return self.env.ref('purchase_stock.route_warehouse0_buy',
                            raise_if_not_found=False).id

    @api.multi
    def _get_vals_for_proc_rule_subcontracting(self):
        self.ensure_one()
        picking_type = self.in_type_id

        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'),
                 '|',
                 ('warehouse_id', '=', self.id),
                 ('warehouse_id', '=', False),
                 ],
                order='warehouse_id asc',
                limit=1
            )
        return {'name': '%s: Subcontracting service rule' % self.name,
                'company_id': self.company_id.id,
                'action': 'buy',
                'picking_type_id': picking_type.id,
                'route_id': self._get_buy_route(),
                'location_id': picking_type.default_location_dest_id.id,
                }

    @api.multi
    def _set_subcontracting_service_proc_rule(self):
        for rec in self:
            if not rec.subcontracting_service_proc_rule_id:
                vals = rec._get_vals_for_proc_rule_subcontracting()
                rule = self.env['stock.rule'].create(vals)
                rec.subcontracting_service_proc_rule_id = rule.id
        return True

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(StockWarehouse, self).create(vals)
        res._set_subcontracting_service_proc_rule()
        return res
