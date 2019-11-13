# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    purchase_ids = fields.One2many(
        default=lambda self: self._context.get('active_ids', []),
    )
    line_ids = fields.One2many(
        default=lambda self: self._get_line(),
    )
    from_rfq = fields.Boolean(
        default=False,
        readonly=True,
        help="True, if this purchase agreement is created from RFQs",
    )

    @api.multi
    def _get_line(self):
        if self._context.get('active_ids'):
            orders = self.env['purchase.order'].browse(
                self._context.get('active_ids', []))
            if orders.mapped('requisition_id'):
                raise ValidationError(_(
                    'Order: %s, was used in some agreement!') % ', '.join(
                    orders.filtered(lambda l: l.requisition_id).mapped('name')))
            po_dict = {}
            len_max = 0
            for order in orders:
                if order.state != 'draft':
                    raise ValidationError(_('The purchase agreement cannot be '
                                            'processed because the order is '
                                            'not in draft!'))
                # Test combination of product and quantity
                po_dict[order.id] = [(line.product_id.id, line.product_qty)
                                     for line in order.order_line]
                if len(po_dict[order.id]) > len_max:
                    id_max = order.id
                    len_max = len(po_dict[order.id])
            test_po = po_dict.pop(id_max)
            for test_line in test_po:
                for key in po_dict.keys():
                    if (po_dict[key].count(test_line) != test_po.count(test_line)):
                        raise ValidationError(_('The purchase agreement cannot be '
                                                'processed because the order '
                                                'are different!'))
            return [(0, 0, {'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom.id,
                            'product_qty': line.product_qty,
                            }) for line in order.order_line]
