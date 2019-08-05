# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _add_supplier_to_product(self):
        """Insert a mapping of products to discounts to be picked up
        in supplierinfo's create()"""
        self.ensure_one()
        discount2_map = dict(
            [(line.product_id.product_tmpl_id.id, line.discount2)
             for line in self.order_line.filtered('discount2')])
        discount3_map = dict(
            [(line.product_id.product_tmpl_id.id, line.discount3)
             for line in self.order_line.filtered('discount3')])
        return super(PurchaseOrder, self.with_context(
            discount2_map=discount2_map, discount3_map=discount3_map)
            )._add_supplier_to_product()


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount2', 'discount3')
    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()

    discount2 = fields.Float(
        'Disc. 2 (%)',
        digits=dp.get_precision('Discount'),
    )

    discount3 = fields.Float(
        'Disc. 3 (%)',
        digits=dp.get_precision('Discount'),
    )

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Discount 2 must be lower than 100%.'),
        ('discount3_limit', 'CHECK (discount3 <= 100.0)',
         'Discount 3 must be lower than 100%.'),
    ]

    def _get_discounted_price_unit(self):
        price_unit = super(
            PurchaseOrderLine, self)._get_discounted_price_unit()
        if self.discount2:
            price_unit *= (1 - self.discount2 / 100.0)
        if self.discount3:
            price_unit *= (1 - self.discount3 / 100.0)
        return price_unit

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
                self.discount2 = product_supplierinfo.discount2
                self.discount3 = product_supplierinfo.discount3
        return res
