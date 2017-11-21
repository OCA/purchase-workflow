# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, _
from odoo.exceptions import UserError
from odoo.addons.purchase.models.purchase import ProcurementRule


def post_load_hook():

    @api.multi
    def _new_run_buy(self, product_id, product_qty, product_uom,
                     location_id, name, origin, values):
        if not hasattr(self, '_prepare_purchase_order_line_update'):
            return self._original_run_buy(
                product_id, product_qty, product_uom, location_id, name,
                origin, values)
        cache = {}
        suppliers = product_id.seller_ids\
            .filtered(lambda r: (
                      not r.company_id or r.company_id == values[
                          'company_id']) and (not r.product_id or
                                              r.product_id == product_id))
        if not suppliers:
            msg = _('There is no vendor associated to the product %s. '
                    'Please define a vendor for this product.') % (
                product_id.display_name,)
            raise UserError(msg)

        supplier = self._make_po_select_supplier(values, suppliers)
        partner = supplier.name

        domain = self._make_po_get_domain(values, partner)

        if domain in cache:
            po = cache[domain]
        else:
            po = self.env['purchase.order'].search([dom for dom in domain])
            po = po[0] if po else False
            cache[domain] = po
        if not po:
            vals = self._prepare_purchase_order(
                product_id, product_qty, product_uom, origin, values, partner)
            po = self.env['purchase.order'].create(vals)
            cache[domain] = po
        elif not po.origin or origin not in po.origin.split(', '):
            if po.origin:
                if origin:
                    po.write({'origin': po.origin + ', ' + origin})
                else:
                    po.write({'origin': po.origin})
            else:
                po.write({'origin': origin})

        # Create Line
        po_line = False
        for line in po.order_line:
            if line.product_id == product_id and \
                    line.product_uom == product_id.uom_po_id:
                if line._merge_in_existing_line(
                        product_id, product_qty, product_uom,
                        location_id, name, origin, values):
                    procurement_uom_po_qty = \
                        product_uom._compute_quantity(product_qty,
                                                      product_id.uom_po_id)
                    seller = product_id._select_seller(
                        partner_id=partner,
                        quantity=line.product_qty + procurement_uom_po_qty,
                        date=po.date_order and po.date_order[:10],
                        uom_id=product_id.uom_po_id)

                    price_unit = self.env['account.tax'].\
                        _fix_tax_included_price_company(
                        seller.price, line.product_id.supplier_taxes_id,
                        line.taxes_id, values['company_id']) if \
                        seller else 0.0
                    if price_unit and seller and po.currency_id and \
                            seller.currency_id != po.currency_id:
                        price_unit = seller.currency_id.compute(
                            price_unit, po.currency_id)

                    po_line = line.write(
                        self._prepare_purchase_order_line_update(
                            line, procurement_uom_po_qty, price_unit, values))
                    break
        if not po_line:
            vals = self._prepare_purchase_order_line(
                product_id, product_qty, product_uom, values, po, supplier)
            self.env['purchase.order.line'].create(vals)

    if not hasattr(ProcurementRule, '_original_run_buy'):
        ProcurementRule._original_run_buy = \
            ProcurementRule._run_buy

        ProcurementRule._run_buy = _new_run_buy
