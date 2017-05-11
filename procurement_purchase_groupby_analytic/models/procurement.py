# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    account_analytic_id = fields.Many2one(
        compute='_compute_analytic_id',
        comodel_name='account.analytic.account')

    @api.one
    @api.depends('sale_line_id.order_id.project_id', 'group_id')
    def _compute_analytic_id(self):
        analytic = None
        if self.sale_line_id:
            analytic = self.sale_line_id.order_id.project_id.id
        elif self.group_id:
            so = self.env['sale.order'].search(
                [('procurement_group_id', '=', self.group_id.id)])
            if so and len(so) == 1:
                analytic = so.project_id.id
        self.account_analytic_id = analytic

    @api.multi
    def _run(self):
        return super(ProcurementOrder, self.with_context(
            account_analytic_id=self.account_analytic_id.id))._run()

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):

        """ If account analytic is defined on procurement order
            set it on purchase order line
        """
        line_vals = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier)
        line_vals['account_analytic_id'] = self.account_analytic_id \
            and self.account_analytic_id.id
        return line_vals
