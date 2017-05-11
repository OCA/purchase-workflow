# -*- coding: utf-8 -*-
# © 2016 Denis Roussel, ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp


from datetime import datetime

UNIT = dp.get_precision('Product Unit of Measure')


class PurchaseImportProducts(models.TransientModel):
    _name = 'purchase.import.products'
    _description = 'Purchase Import Products'

    products = fields.Many2many(
        comodel_name='product.product', string="Products")
    items = fields.One2many(
        comodel_name='purchase.import.products.items',
        inverse_name='wizard_id')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Supplier')

    @api.multi
    def create_items(self):
        self.ensure_one()
        for product in self.products:
            self.env['purchase.import.products.items'].create({
                'wizard_id': self.id,
                'product_id': product.id
            })
        ctx = self.env.context.copy()
        ctx['mode'] = 'quantity'
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': ctx,
        }

    @api.model
    def _get_line_values(self, purchase, item):
        """
        @param purchase: implied purchase order
        @type purchase: purchase.order recordset
        @param item: item to
        @type item: purchase.import.products.items recordset
        @rparam: values to create purchase order line with the product item and
        the right quantity
        @rtype: dict
        """
        return {
            'order_id': purchase.id,
            'name': item.product_id.name,
            'product_id': item.product_id.id,
            'product_qty': item.quantity or 1,
            'product_uom': item.product_id.uom_po_id.id,
            'price_unit': 0.0,
            'date_planned': datetime.today().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
        }

    @api.multi
    def select_products(self):
        if not self.env.context.get('active_id') or\
                not self.env.context.get('active_model'):
            raise UserError(_('Should have an id of purchase order'))
        self.ensure_one()
        po_obj = self.env['purchase.order']
        purchase_id = po_obj.browse(self.env.context.get('active_id'))
        for item in self.items:
            vals = self._get_line_values(purchase_id, item)
            po_line = self.env['purchase.order.line'].create(vals)
            po_line.onchange_product_id()
            po_line.product_qty = item.quantity
        return {'type': 'ir.actions.act_window_close', }


class PurchaseImportProductsItem(models.TransientModel):
    _name = 'purchase.import.products.items'

    wizard_id = fields.Many2one(
        comodel_name='purchase.import.products', string="Wizard",)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        required=True, ondelete='cascade')
    quantity = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0, string='Quantity', required=True, ondelete='cascade')
