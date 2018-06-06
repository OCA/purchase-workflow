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

    @api.multi
    def _get_sale_order_domain(self):
        return [('procurement_group_id', 'in', self.mapped('group_id.id'))]

    @api.multi
    @api.depends('sale_line_id.order_id.project_id', 'group_id')
    def _compute_analytic_id(self):
        procurements = self.filtered(lambda p: p.sale_line_id or p.group_id)
        procurements_w_group = procurements.filtered(lambda p: p.group_id)
        # Avoid multiple searches in loop
        sale_orders = self.env['sale.order'].search(
            procurements_w_group._get_sale_order_domain()
        )
        for procurement in procurements:
            analytic = None
            if procurement.sale_line_id:
                analytic = procurement.sale_line_id.order_id.project_id
            elif procurement.group_id:
                so = sale_orders.filtered(
                    lambda s, p=procurement: s.procurement_group_id ==
                    p.group_id)
                if so and len(so) == 1:
                    analytic = so.project_id
            procurement.account_analytic_id = analytic

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):

        """ If account analytic is defined on procurement order
            set it on purchase order line
        """
        line_vals = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier)
        if self.account_analytic_id:
            line_vals['account_analytic_id'] = self.account_analytic_id.id
        return line_vals

    @api.multi
    def _make_po_get_domain(self, partner):
        self.ensure_one()
        res = super(ProcurementOrder, self)._make_po_get_domain(
            partner=partner)
        if self.account_analytic_id:
            res += (('order_line.account_analytic_id',
                    '=',
                    self.account_analytic_id.id),)
        return res
