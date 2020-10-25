# Copyright 2019 Jarsa Sistemas S.A. de C.V.
# Copyright 2020 MtNet Services S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _prepare_sellers(self, params):
        res = super()._prepare_sellers(params)
        if not params:
            return res
        if params.get('supplier'):
            currency_id = params.get('supplier').currency_id.id
        else:
            currency_id = params.get('order_id').partner_id.currency_id.id
        return res.with_context(currency_id=currency_id).filtered(
            lambda s: s.currency_id.id == currency_id)
