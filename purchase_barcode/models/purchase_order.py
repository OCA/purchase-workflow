# -*- coding: utf-8 -*-
# Copyright 2017 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _barcode_scanned = fields.Char("Barcode Scanned",
                                   help="Value of the last barcode scanned.",
                                   store=False)

    @api.model
    def po_barcode(self, barcode, po_id):
        purchase_order = self.search([('id', '=', po_id)])
        if not purchase_order:
            # with asumtation Purchase Order is created
            raise UserError(_('Please Choose Your Vendor And Fix Your Purchase Order'))
        product_id = self.env['product.product'].search([('barcode', '=', barcode)])
        purchase_order_line = purchase_order.order_line.search([('product_id', '=', product_id.id)], limit=1)
        if purchase_order_line:
            purchase_order_line.product_qty = purchase_order_line.product_qty + 1
        else:
            line_values = {
                'name': product_id.name,
                'product_id': product_id.id,
                'product_qty': 1,
                'product_uom': product_id.product_tmpl_id.uom_id.id,
                'price_unit': product_id.product_tmpl_id.list_price,
                'order_id': purchase_order.id,
                'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}
            purchase_order.update({'order_line': [(0, 0, line_values)]})
