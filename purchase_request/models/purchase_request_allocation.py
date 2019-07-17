# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class PurchaseRequestAllocation(models.Model):
    _name = 'purchase.request.allocation'
    _description = 'Purchase Request Allocation'

    purchase_request_line_id = fields.Many2one(
        string='Purchase Request Line',
        comodel_name='purchase.request.line',
        required=True, ondelete='cascade',
        copy=False,
    )
    company_id = fields.Many2one(string='Company',
                                 comodel_name='res.company',
                                 readonly=True,
                                 related='purchase_request_line_id.request_id.'
                                         'company_id'
                                 )
    stock_move_id = fields.Many2one(string='Stock Move',
                                    comodel_name='stock.move',
                                    copy=False,
                                    required=True, ondelete='cascade',
                                    )
    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product',
                                 related='purchase_request_line_id.product_id',
                                 readonly=True,
                                 )
    product_uom_id = fields.Many2one(
        string='UoM', comodel_name='product.uom',
        related='purchase_request_line_id.product_uom_id',
        readonly=True,
        )
    requested_product_uom_qty = fields.Float(
        'Requested Quantity (UoM)',
        help='Quantity of the purchase request line allocated to the'
             'stock move, in the UoM of the Purchase Request Line',
    )
    requested_product_qty = fields.Float(
        'Requested Quantity',
        help='Quantity of the purchase request line allocated to the stock'
             'move, in the default UoM of the product',
        compute='_compute_requested_product_qty'
    )
    allocated_product_qty = fields.Float(
        'Allocated Quantity',
        copy=False,
        help='Quantity of the purchase request line allocated to the stock'
             'move, in the default UoM of the product',
    )
    open_product_qty = fields.Float('Open Quantity',
                                    compute='_compute_open_product_qty')

    @api.depends('purchase_request_line_id.product_id',
                 'purchase_request_line_id.product_uom_id',
                 'purchase_request_line_id')
    def _compute_requested_product_qty(self):
        for rec in self:
            rec.requested_product_qty = rec.product_uom_id._compute_quantity(
                rec.requested_product_uom_qty, rec.product_id.uom_id)

    @api.depends('requested_product_qty', 'allocated_product_qty',
                 'stock_move_id', 'stock_move_id.state')
    def _compute_open_product_qty(self):
        for rec in self:
            if rec.stock_move_id.state in ['cancel', 'done']:
                rec.open_product_qty = 0.0
            else:
                rec.open_product_qty = \
                    rec.requested_product_qty - rec.allocated_product_qty
                if rec.open_product_qty < 0.0:
                    rec.open_product_qty = 0.0
