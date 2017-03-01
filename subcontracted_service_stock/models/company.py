# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.multi
    def _get_vals_for_proc_rule_subcontracting(self):
        self.ensure_one()
        res = super(ResCompany, self)._get_vals_for_proc_rule_subcontracting()
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
        res.update(picking_type_id=picking_type.id)
        return res
