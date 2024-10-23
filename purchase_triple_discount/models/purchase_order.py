# Copyright 2017-19 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_supplier_info(self, partner, line, price, currency):
        res = super()._prepare_supplier_info(partner, line, price, currency)
        res.update(
            dict(
                (fname, line[fname])
                for fname in line._get_multiple_discount_field_names()
            )
        )
        res.pop("discount")
        return res
