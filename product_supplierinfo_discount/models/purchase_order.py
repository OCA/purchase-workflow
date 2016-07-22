# -*- coding: utf-8 -*-
# Copyright (c) 2016 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                    Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#                    Andrius Preimantas <andrius@versada.lt>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _get_product_discount(self, product_id, qty, partner_id):
        """Return discount for provided qty and supplier or None otherwise."""
        supplierinfo_obj = self.env['product.supplierinfo']
        product_obj = self.env['product.product']
        product_uom_obj = self.env['product.uom']
        pl_pinfo_obj = self.env['pricelist.partnerinfo']
        res = None
        product = product_obj.browse(product_id)
        from_uom = self.env.context.get('uom') or product.uom_id.id
        qty_in_product_uom = qty
        partner = self.env['res.partner'].browse(partner_id)
        sinfos = supplierinfo_obj.search(
            [('product_tmpl_id', '=', product.product_tmpl_id.id),
             ('name', 'child_of', partner.commercial_partner_id.id)])
        if not sinfos:
            return res
        seller_uom = sinfos[:1].product_uom.id or False
        if seller_uom and from_uom and from_uom != seller_uom:
            qty_in_product_uom = product_uom_obj._compute_qty(
                from_uom, qty, to_uom_id=seller_uom)
        pl_pinfos = pl_pinfo_obj.search(
            [('suppinfo_id', 'in', sinfos.ids)], order="min_quantity")

        for pl_pinfo in pl_pinfos:
            if pl_pinfo.min_quantity <= qty_in_product_uom:
                res = pl_pinfo.discount
            else:
                break
        return res

    @api.multi
    def onchange_product_id(
            self, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty, uom_id, partner_id,
            date_order=date_order, fiscal_position_id=fiscal_position_id,
            date_planned=date_planned, name=name, price_unit=price_unit,
            state=state)
        if not product_id:
            return res
        # Look for a possible discount
        discount = self._get_product_discount(product_id, qty, partner_id)
        if discount is not None:
            val = res.setdefault('value', {})
            val['discount'] = discount
        return res
