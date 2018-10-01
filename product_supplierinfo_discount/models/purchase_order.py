# Copyright 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _add_supplier_to_product(self):
        """ Insert a mapping of products to discounts to be picked up
        in supplierinfo's create() """
        self.ensure_one()
        discount_map = dict(
            [(line.product_id.product_tmpl_id.id, line.discount)
             for line in self.order_line.filtered('discount')])
        return super(PurchaseOrder, self.with_context(
            discount_map=discount_map))._add_supplier_to_product()


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        """
        Check if a discount is defined into the supplier info and if so then
        apply it to the current purchase order line
        """
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        if self.product_id:
            date = None
            if self.order_id.date_order:
                date = fields.Date.to_string(
                    fields.Date.from_string(self.order_id.date_order))
            product_supplierinfo = self.product_id._select_seller(
                partner_id=self.partner_id, quantity=self.product_qty,
                date=date, uom_id=self.product_uom)
            if product_supplierinfo:
                self.discount = product_supplierinfo.discount
        return res
