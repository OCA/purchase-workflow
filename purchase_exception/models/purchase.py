# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, models

logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = ['purchase.order', 'base.exception']
    _name = 'purchase.order'
    _order = 'main_exception_id asc, date_order desc, name desc'

    @api.model
    def test_all_draft_orders(self):
        order_set = self.search([('state', '=', 'draft')])
        order_set.detect_exceptions()
        return True

    @api.model
    def _exception_rule_eval_context(self, rec):
        # TODO remove in v13
        # We keep this only for backward compatibility
        res = super()._exception_rule_eval_context(rec)
        if res.get("purchase"):
            logger.warning("""
                For a full compatibility with future versions of this module,
                please use 'self' instead of 'purchase' in your
                custom exceptions rules.
                """)
        res['purchase'] = rec
        return res

    @api.model
    def _reverse_field(self):
        return 'purchase_ids'

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
        lines = self.mapped('order_line')
        all_exceptions += lines.detect_exceptions()
        return all_exceptions

    @api.constrains('ignore_exception', 'order_line', 'state')
    def purchase_check_exception(self):
        orders = self.filtered(lambda s: s.state == 'purchase')
        if orders:
            orders._check_exception()

    @api.onchange('order_line')
    def onchange_ignore_exception(self):
        if self.state == 'purchase':
            self.ignore_exception = False

    @api.multi
    def button_confirm(self):
        if self.detect_exceptions() and not self.ignore_exception:
            return self._popup_exceptions()
        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def button_draft(self):
        res = super(PurchaseOrder, self).button_draft()
        for order in self:
            order.exception_ids = False
            order.main_exception_id = False
            order.ignore_exception = False
        return res

    @api.model
    def _get_popup_action(self):
        action = self.env.ref(
            'purchase_exception.action_purchase_exception_confirm')
        return action
