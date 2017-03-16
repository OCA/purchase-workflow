# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models
from odoo import _


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    @api.multi
    def _compute_has_purchase_request_lines(self):
        for rec in self:
            rec.has_purchase_request_lines = bool(rec.purchase_request_lines)

    purchase_request_lines = fields.Many2many(
        'purchase.request.line',
        'purchase_request_purchase_requisition_line_rel',
        'purchase_requisition_line_id',
        'purchase_request_line_id',
        string='Purchase Request Lines', readonly=True, copy=False)
    has_purchase_request_lines = fields.Boolean(
        string="Has Purchase Request Lines",
        compute="_compute_has_purchase_request_lines"
        )

    @api.multi
    def action_openRequestLineTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids = [request_line.id for request_line
                                in line.purchase_request_lines]
        domain = [('id', 'in', request_line_ids)]

        return {'name': _('Purchase Request Lines'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request.line',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': domain}

    @api.multi
    def _prepare_purchase_order_line(self, name, product_qty=0.0,
                                     price_unit=0.0, taxes_ids=False):
        res = super(PurchaseRequisitionLine, self). \
            _prepare_purchase_order_line(
            name, product_qty=product_qty, price_unit=price_unit,
            taxes_ids=taxes_ids)
        res.update({
            'purchase_request_lines':
                [(4, line.id) for line in self.purchase_request_lines],
        })
        return res
