# -*- coding: utf-8 -*-
# © 2016 Denis Roussel, ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from lxml import etree

UNIT = dp.get_precision('Product Unit of Measure')


class PurchaseImportProducts(models.TransientModel):
    _name = 'purchase.import.products'
    _description = 'Purchase Import Products'

    quantity = fields.Float(string='Quantity', digits_compute=UNIT,
                            default=1.0)
    products = fields.Many2many(comodel_name='product.product',
                                string="Products")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(PurchaseImportProducts,
                    self).fields_view_get(view_id=view_id, view_type=view_type,
                                          toolbar=toolbar, submenu=False)
        if view_type == 'form':
            model = self.env.context.get('active_model', False)
            model_id = self.env.context.get('active_id', False)
            if model and model == 'purchase.order' and model_id:
                purchase = self.env['purchase.order'].browse(model_id)
                if purchase and purchase.partner_id:
                    doc = etree.XML(res['arch'])
                    nodes = doc.xpath("//field[@name='products']")
                    for node in nodes:
                        node.set('domain', '[("seller_ids.name", "=", ' +
                                 str(purchase.partner_id.id) + ')]')
                res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def select_products(self):
        po_obj = self.env['purchase.order']
        for wizard in self:
            purchase = po_obj.browse(self.env.context.get('active_id', False))

            if purchase:
                for product in wizard.products:
                    if wizard.quantity:
                        quantity = wizard.quantity
                    else:
                        quantity = 1
                    pol = self.env['purchase.order.line']
                    position = purchase.fiscal_position.id
                    date_order = purchase.date_order
                    uom = product.uom_po_id
                    suppliers = product.seller_ids.filtered(
                        lambda r: r.name == purchase.partner_id)
                    for supplier in suppliers:
                        uom = supplier.product_uom
                        break

                    onchange_f = pol._model.onchange_product_id

                    vals = onchange_f(self.env.cr, self.env.uid, [],
                                      purchase.pricelist_id.id,
                                      product.id, quantity,
                                      uom.id,
                                      purchase.partner_id.id,
                                      date_order=date_order,
                                      fiscal_position_id=position,
                                      date_planned=False,
                                      name=False, price_unit=False,
                                      state=purchase.state,
                                      context=self.env.context)

                    if 'value' in vals:
                        taxes = vals['value']['taxes_id']
                        vals['value'].update({'order_id': purchase.id,
                                              'product_id': product.id,
                                              'taxes_id': [(6, 0, taxes)]})

                        pol.create(vals['value'])

        return {'type': 'ir.actions.act_window_close', }
