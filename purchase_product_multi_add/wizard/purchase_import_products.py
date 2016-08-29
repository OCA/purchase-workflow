# -*- coding: utf-8 -*-
# © 2016 Denis Roussel, ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

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
        quantity = 1.0
        if item.quantity:
            quantity = item.quantity
        pol = self.env['purchase.order.line']
        position = purchase.fiscal_position.id
        date_order = purchase.date_order
        uom = item.product_id.uom_po_id
        suppliers = item.product_id.seller_ids.filtered(
            lambda r: r.name == purchase.partner_id)
        for supplier in suppliers:
            uom = supplier.product_uom
            break
        onchange_f = pol._model.onchange_product_id
        product = item.product_id
        vals = onchange_f(
            self.env.cr, self.env.uid, [], purchase.pricelist_id.id,
            product.id, quantity, uom.id, purchase.partner_id.id,
            date_order=date_order, fiscal_position_id=position,
            date_planned=False, name=False, price_unit=False,
            state=purchase.state, context=self.env.context)
        if 'value' in vals:
            taxes = vals['value']['taxes_id']
            vals['value'].update({
                'order_id': purchase.id,
                'product_id': product.id,
                'taxes_id': [(6, 0, taxes)]
            })
            vals = vals['value']
        return vals

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
            self.env['purchase.order.line'].create(vals)
        return {'type': 'ir.actions.act_window_close', }


class PurchaseImportProductsItem(models.TransientModel):
    _name = 'purchase.import.products.items'

    wizard_id = fields.Many2one(
        comodel_name='purchase.import.products', string="Wizard",)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        required=True, ondelete='cascade')
    quantity = fields.Float(
        digits_compute=dp.get_precision('Product Unit of Measure'),
        default=1.0, string='Quantity', required=True, ondelete='cascade')
