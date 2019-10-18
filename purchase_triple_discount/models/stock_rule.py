# Copyright 2019 GRAP (http://www.grap.coop)
# Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _prepare_purchase_order_line_from_seller(self, seller):
        res = super()._prepare_purchase_order_line_from_seller(seller)
        if res:
            res.update({
                'discount2': seller.discount2,
                'discount3': seller.discount3,
            })
        return res
