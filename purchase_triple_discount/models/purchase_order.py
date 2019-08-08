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

    # adding discount2 and discount3 to depends
    @api.depends('discount2', 'discount3')
    def _compute_amount(self):
        super()._compute_amount()

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
        price_unit = super()._get_discounted_price_unit()
        if self.discount2:
            price_unit *= (1 - self.discount2 / 100.0)
        if self.discount3:
            price_unit *= (1 - self.discount3 / 100.0)
        return price_unit

    @api.model
    def _apply_value_from_seller(self, seller):
        super()._apply_value_from_seller(seller)
        if not seller:
            return
        self.discount2 = seller.discount2
        self.discount3 = seller.discount3
