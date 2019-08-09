# Copyright 2019 GRAP (http://www.grap.coop)
# Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models
import odoo.addons.decimal_precision as dp


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    discount2 = fields.Float(
        string='Discount 2 (%)', digits=dp.get_precision('Discount'),
        group_operator="avg",
    )
    discount3 = fields.Float(
        string='Discount 3 (%)', digits=dp.get_precision('Discount'),
        group_operator="avg",
    )

    def _select(self):
        res = super()._select()
        res += ", l.discount2 AS discount2, l.discount3 AS discount3"
        return res

    def _group_by(self):
        res = super()._group_by()
        res += ", l.discount2, l.discount3"
        return res

    def _get_discounted_price_unit_exp(self):
        """Inheritable method for getting the SQL expression used for
        calculating the unit price with discount(s).

        :rtype: str
        :return: SQL expression for discounted unit price.
        """
        return """
            ((100 - COALESCE(l.discount, 0.0)) *
             (100 - COALESCE(l.discount2, 0.0)) *
             (100 - COALESCE(l.discount3, 0.0))) / 1000000 * l.price_unit"""
