# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business, IT Consulting Services S.L. and ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _name = "purchase.request.line.make.purchase.requisition.item"
    _description = "Purchase Request Line Make Purchase Requisition Item"

    wiz_id = fields.Many2one(
        'purchase.request.line.make.purchase.requisition',
        string='Wizard', required=True, ondelete='cascade',
        readonly=True)
    line_id = fields.Many2one('purchase.request.line',
                              string='Purchase Request Line',
                              required=True,
                              readonly=True)
    request_id = fields.Many2one('purchase.request',
                                 related='line_id.request_id',
                                 string='Purchase Request',
                                 readonly=True)
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description', required=True)
    product_qty = fields.Float(string='Quantity to Bid',
                               digits=dp.get_precision('Product UoS'))
    product_uom_id = fields.Many2one('product.uom', string='UoM')

    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
