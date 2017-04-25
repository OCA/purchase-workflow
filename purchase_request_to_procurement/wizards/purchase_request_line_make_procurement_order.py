# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class PurchaseRequestLineMakeProcurementOrder(models.TransientModel):

    _name = 'purchase.request.line.make.procurement.order'
    _description = 'Purchase Request Line Make Procurement Order'

    @api.model
    def _get_domain(self):
        return [
            ('request_state', '=', 'approved'),
            ('product_id', '!=', False)]

    @api.model
    def _get_default_request_line(self):
        active_ids = self.env.context.get('active_ids')
        domain = [('id', 'in', active_ids)]
        domain += self._get_domain()
        res_ids = self.env[
            self.purchase_request_line_m2m_ids._name].search(domain)
        return [(6, False, res_ids.ids)]

    purchase_request_line_m2m_ids = fields.Many2many(
        comodel_name='purchase.request.line',
        column1='wizard_id',
        column2='pr_line_id',
        relation='wizard_id_pr_line_id_rel', string='Items',
        default=_get_default_request_line,
        domain=_get_domain,)

    @api.multi
    def make_procurement_order(self):
        """
        wizard object action to launch the generation of the procurement order
        """
        procurement_ids = []
        for wizard in self:
            for item in wizard.purchase_request_line_m2m_ids:
                if not item.procurement_id:
                    p_order_id = item._generate_procurement_order()
                    item.procurement_id = p_order_id
                    procurement_ids.append(p_order_id)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Generated Procurement Order',
            'res_model': 'procurement.order',
            'domain': [('id', 'in', procurement_ids)],
            'view_mode': 'tree,form',
        }
        return action
