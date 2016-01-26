# -*- coding: utf-8 -*-
# (c) 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft'
    ):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id=pricelist_id, product_id=product_id, qty=qty,
            uom_id=uom_id, partner_id=partner_id, date_order=date_order,
            fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, state=state)
        if product_id:
            product_model = self.env['product.product']
            if self.user_has_groups(
                    'purchase_order_line_description.'
                    'group_use_product_description_per_po_line'):
                lang = self.env['res.partner'].browse(partner_id).lang
                product = product_model.with_context(lang=lang).browse(
                    product_id)
                if product.description_purchase:
                    if 'value' not in res:
                        res['value'] = {}
                    res['value']['name'] = product.description_purchase
        return res
