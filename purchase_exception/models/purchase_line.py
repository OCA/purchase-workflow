# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = ["purchase.order.line", "base.exception.method"]
    _name = "purchase.order.line"

    ignore_exception = fields.Boolean(
        related="order_id.ignore_exception", store=True, string="Ignore Exceptions"
    )

    @api.multi
    def _get_main_records(self):
        return self.mapped("order_id")

    @api.model
    def _reverse_field(self):
        return "purchase_ids"

    @api.multi
    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        return records.mapped("order_id")

    @api.model
    def _exception_rule_eval_context(self, rec):
        # TODO remove in v13
        # We keep this only for backward compatibility, because some existing
        # rules may use the variable "purchase_line". But we should remove this
        # code during v13 migration.
        res = super()._exception_rule_eval_context(rec)
        if res.get("purchase_line"):
            logger.warning(
                """
                For a full compatibility with future versions of this module,
                please use 'self' instead of 'purchase_line' in your
                custom exceptions rules.
                """
            )
        res["purchase_line"] = rec
        return res
