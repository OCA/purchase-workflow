# Copyright 2019 Jarsa Sistemas S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# pylint: disable=C0103

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_get_domain(self, values, partner):
        domain = super(StockRule, self)._make_po_get_domain(values, partner)
        supplier = values.get('supplier')
        if supplier and supplier.currency_id:
            domain += (('currency_id', '=', supplier.currency_id.id),)
        return domain

    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po, partner):
        """Method overridden from odoo to set the proper product unit price
        taking in consideration the product supplier info price"""
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner)
        procurement_uom_po_qty = product_uom._compute_quantity(
            product_qty, product_id.uom_po_id)
        seller = product_id._select_seller(
            partner_id=partner,
            quantity=procurement_uom_po_qty,
            date=po.date_order and po.date_order.date(),
            uom_id=product_id.uom_po_id,
            params=values)
        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(
            taxes, product_id, seller.name) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(
                lambda x: x.company_id.id == values['company_id'].id)
        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            seller.price, product_id.supplier_taxes_id,
            taxes_id, values['company_id']) if seller else 0.0

        # Search if a RFQ with the supplierinfo currency exists if, there
        # is not we create a new PO with the supplierinfo currency
        domain = self._make_po_get_domain(values, partner)
        purchase_order = self.env['purchase.order'].sudo().search(
            [dom for dom in domain])
        if not purchase_order:
            group_id = values.get('group_id')
            if group_id:
                origin = group_id.name
            vals = self._prepare_purchase_order(
                product_id, product_qty, product_uom, origin, values, partner)
            company_id = values.get('company_id') and values[
                'company_id'].id or self.env.user.company_id.id
            po = self.env['purchase.order'].with_context(
                force_company=company_id).sudo().create(vals)
        res.update({
            'price_unit': price_unit,
            'order_id': po.id,
        })
        return res

    def _prepare_purchase_order(self, product_id, product_qty,
                                product_uom, origin, values, partner):
        """Method overridden from odoo to set the proper PO currency
        taking in consideration the product supplier info currency"""
        res = super()._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, partner)
        seller = values.get('supplier')
        seller_currency_id = seller.currency_id.id
        supplier_currency_id = partner.with_context(force_company=values[
            'company_id'].id).property_purchase_currency_id.id
        company_currency_id = self.env.user.company_id.currency_id.id
        res['currency_id'] = (
            seller_currency_id or supplier_currency_id or company_currency_id)
        return res
