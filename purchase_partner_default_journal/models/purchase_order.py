# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        # pylint: disable=R8110
        # v7 api because super does it
        result = super(PurchaseOrder, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context
        )
        if not partner_id:
            return result
        result.get('value')['journal_id'] = self.pool['res.partner'].browse(
            cr, uid, partner_id, context=context
        ).default_purchase_journal_id.id
        return result

    @api.model
    def _prepare_invoice(self, order, line_ids):
        result = super(PurchaseOrder, self)._prepare_invoice(order, line_ids)
        result['journal_id'] = order.journal_id.id or\
            order.partner_id.default_purchase_journal_id.id
        return result
