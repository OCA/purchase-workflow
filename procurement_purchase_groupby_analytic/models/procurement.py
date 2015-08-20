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


from openerp import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    account_analytic_id = fields.Many2one(
        compute='_compute_analytic_id',
        comodel_name='account.analytic.account')

    @api.one
    @api.depends('sale_line_id.order_id.project_id',
                 'group_id')
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

    @api.model
    def _get_available_draft_po_domain(self, procurement, partner):
        """ If account analytic is defined on procurement order
            search draft purchase order on this criteria
        """
        available_draft_po_domain = super(
            ProcurementOrder, self)._get_available_draft_po_domain(
                procurement, partner)
        available_draft_po_domain.append(
            ('order_line.account_analytic_id', '=',
             procurement.account_analytic_id.id))

        return available_draft_po_domain

    @api.model
    def create_procurement_purchase_order(self, procurement, po_vals,
                                          line_vals):
        """ If account analytic is defined on procurement order
            set it on purchase order line
        """
        line_vals['account_analytic_id'] = procurement.account_analytic_id \
            and procurement.account_analytic_id.id
        return super(
            ProcurementOrder, self).create_procurement_purchase_order(
                procurement, po_vals, line_vals)
