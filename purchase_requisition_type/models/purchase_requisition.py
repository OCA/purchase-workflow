# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.addons.purchase.purchase import purchase_order


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def _default_order_type(self):
        return self.env['purchase.order.type'].search([], limit=1)

    order_type = fields.Many2one(comodel_name='purchase.order.type',
                                 readonly=False,
                                 states=purchase_order.READONLY_STATES,
                                 string='Type',
                                 ondelete='restrict',
                                 default=_default_order_type)

    @api.model
    def _prepare_purchase_order(self, requisition, supplier):
        res = super(PurchaseRequisition, self)._prepare_purchase_order(
            requisition, supplier)

        if requisition.order_type:
            res.update({
                'order_type': requisition.order_type.id,
                'invoice_method': requisition.order_type.invoice_method})

        return res
