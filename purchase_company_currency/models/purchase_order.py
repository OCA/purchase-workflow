# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Company Currency",
        readonly=True
    )
    amount_total_curr = fields.Monetary(
        string="Total Amount",
        readonly=True,
        help='Sale Order Amount in the company Currency',
        compute="_compute_amount_company",
        currency_id='company_currency_id',
    )

    @api.multi
    @api.depends('amount_total')
    def _compute_amount_company(self):
        for po in self:
            if po.state in ('purchase', 'done'):
                po_date = po.confirmation_date
            else:
                po_date = po.date_order
            po.amount_total_curr = po.currency_id.with_context(
                date=po_date).compute(
                po.amount_total, po.company_id.currency_id)
