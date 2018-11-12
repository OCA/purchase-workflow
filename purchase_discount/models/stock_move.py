# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.
        """
        self.ensure_one()
        price = super(StockMove, self)._get_price_unit()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            price = price * (1 - self.purchase_line_id.discount / 100)
        return price
