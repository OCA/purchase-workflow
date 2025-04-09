# Copyright 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    discount = fields.Float(string="Discount (%)", digits="Discount", aggregator="avg")

    def _select(self):
        select_sql = super()._select()
        # There are 3 matches
        res = select_sql.code.replace(
            "l.price_unit", self._get_discounted_price_unit_exp()
        )
        res += ", l.discount AS discount"
        return SQL(res, *select_sql.params)

    def _group_by(self):
        group_sql = super()._group_by()
        code = group_sql.code + ", l.discount"
        return SQL(code, *group_sql.params)

    def _get_discounted_price_unit_exp(self):
        """Inheritable method for getting the SQL expression used for
        calculating the unit price with discount(s).

        :rtype: str
        :return: SQL expression for discounted unit price.
        """
        return "(1.0 - COALESCE(l.discount, 0.0) / 100.0) * l.price_unit"
