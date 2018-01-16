# Copyright 2018 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _add_supplier_to_product(self):
        """Update the partner info in the supplier list of the product if the
        supplier is registered for this product."""
        super(PurchaseOrder, self)._add_supplier_to_product()
        for line in self.order_line:
            partner = (
                self.partner_id if not self.partner_id.parent_id
                else self.partner_id.parent_id)
            sellers = line.product_id.seller_ids
            if partner in sellers.mapped('name'):
                currency = (
                    partner.property_purchase_currency_id or
                    self.env.user.company_id.currency_id)
                sellers.filtered(lambda x: x.name == partner).write({
                    'price': self.currency_id.compute(
                        line.price_unit, currency),
                })
