# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import random

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id,
                 name, origin, values):
        grouping = product_id.categ_id.procured_purchase_grouping
        self_wc = self.with_context(grouping=grouping)
        return super(StockRule, self_wc)._run_buy(
            product_id, product_qty, product_uom, location_id, name,
            origin, values)

    def _make_po_get_domain(self, values, partner):
        domain = super()._make_po_get_domain(values, partner)
        if self.env.context.get('grouping', 'standard') == 'product_category':
            if values.get("product_id"):
                product = self.env["product.product"].browse(values["product_id"])
                domain += (
                    ("order_line.product_id.categ_id", "=", product.categ_id.id),
                )
        elif self.env.context.get('grouping', 'standard') == 'order':
            if values.get("move_dest_ids"):
                domain += (("id", "=", -values["move_dest_ids"][:1].id),)
            # The minimum is imposed by PG int4 limit
            domain += (("id", "=", random.randint(-2147483648, 0)),)
        return domain
