# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    subcontracting_service_proc_rule_id = fields.Many2one(
        comodel_name='procurement.rule',
        string="Subcontracting_service procurement rule"
    )

    @api.multi
    def _get_vals_for_proc_rule_subcontracting(self):
        self.ensure_one()
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.id)],
            limit=1
        )
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'),
             ('warehouse_id', '=', warehouse.id)
             ],
            limit=1
        )
        return {'name': 'Subcontracting service rule',
                'company_id': self.id,
                'action': 'buy',
                'is_subcontracting_rule': True,
                'picking_type_id': picking_type.id,
                }

    @api.multi
    def _set_subcontracting_service_proc_rule(self):
        for rec in self:
            if rec.subcontracting_service_proc_rule_id:
                continue

            vals = rec._get_vals_for_proc_rule_subcontracting()
            rule = self.env['procurement.rule'].create(vals)
            rec.subcontracting_service_proc_rule_id = rule.id

        return True

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(ResCompany, self).create(vals)
        res._set_subcontracting_service_proc_rule()
        return res
